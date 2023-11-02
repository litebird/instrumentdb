# -*- encoding: utf-8 -*-
import json
from datetime import datetime
from datetime import timezone
import mimetypes
from math import ceil
from pathlib import Path
from typing import List

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework import viewsets, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

import instrumentdb
from browse.models import Entity, Quantity, DataFile, FormatSpecification, Release
from browse.serializers import (
    UserSerializer,
    GroupSerializer,
    FormatSpecificationSerializer,
    EntitySerializer,
    QuantitySerializer,
    DataFileSerializer,
    ReleaseSerializer,
    UserSigninSerializer,
)

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny

from instrumentdb.authentication import (
    token_expire_handler,
    expires_in,
    is_token_expired,
)

ADMIN_ONLY_HTTP_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

mimetypes.init()


###########################################################################


class UserView(DetailView):
    model = User
    template_name = "browse/user_detail.html"

    def get_object(self):
        obj = get_object_or_404(User, username=self.kwargs["username"])
        return obj


###########################################################################


@login_required
def entity_tree_view(request):
    return render(
        request,
        Path("browse") / "entity_list.html",
        {"object_list": Entity.objects.all()},
    )


class EntityView(DetailView):
    model = Entity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from .custom import create_entity_view_context

        create_entity_view_context(context)

        return context


###########################################################################


class QuantityView(DetailView):
    model = Quantity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from .custom import create_quantity_view_context

        create_quantity_view_context(context)

        return context


###########################################################################


class DataFileView(DetailView):
    model = DataFile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from .custom import create_datafile_view_context

        create_datafile_view_context(context)

        return context


class FormatSpecificationListView(ListView):
    model = FormatSpecification


class FormatSpecificationDownloadView(View):
    def get(self, request, pk):
        "Allow the user to download a data file"

        cur_object = get_object_or_404(FormatSpecification, pk=pk)
        file_data = cur_object.doc_file

        try:
            file_data.open()
        except ValueError:
            raise Http404(
                "The format specification file was not uploaded to the database"
            )

        data = file_data.read()
        resp = HttpResponse(data, content_type=cur_object.doc_mime_type)

        resp["Content-Disposition"] = 'filename="{0}"'.format(
            cur_object.get_sensible_file_name()
        )
        return resp


class DataFileDownloadView(View):
    def get(self, request, pk):
        "Allow the user to download a data file"

        cur_object = get_object_or_404(DataFile, pk=pk)
        file_data = cur_object.file_data
        try:
            file_data.open()
        except ValueError:
            raise Http404("The data file was not uploaded to the database")

        data = file_data.read()
        resp = HttpResponse(
            data, content_type=cur_object.quantity.format_spec.file_mime_type
        )
        resp["Content-Disposition"] = 'attachment; filename="{0}"'.format(
            Path(cur_object.name).name
        )
        return resp


class DataFilePlotDownloadView(View):
    def get(self, request, pk):
        "Allow the user to download the plot associated with a data file"

        cur_object = get_object_or_404(DataFile, pk=pk)
        plot_file_data = cur_object.plot_file

        try:
            plot_file_data.open()
        except ValueError:
            raise Http404("The plot file was not uploaded to the database")

        data = plot_file_data.read()
        resp = HttpResponse(data, content_type=cur_object.plot_mime_type)

        resp["Content-Disposition"] = 'attachment; filename="{name}{ext}"'.format(
            name=Path(cur_object.name).name,
            ext=mimetypes.guess_extension(cur_object.plot_mime_type),
        )
        return resp


class ReleaseDocumentDownloadView(View):
    def get(self, request, pk):
        "Allow the user to download a release document"

        cur_object = get_object_or_404(Release, pk=pk)
        release_document_data = cur_object.release_document

        try:
            release_document_data.open()
        except ValueError:
            raise Http404("The release document was not uploaded to the database")

        data = release_document_data.read()
        resp = HttpResponse(data, content_type=cur_object.release_document_mime_type)

        resp["Content-Disposition"] = 'filename="{name}{ext}"'.format(
            name=cur_object.tag,
            ext=mimetypes.guess_extension(cur_object.release_document_mime_type),
        )
        return resp


###########################################################################


class ReleaseListView(LoginRequiredMixin, ListView):
    model = Release

    ordering = ["-tag"]


class ReleaseView(DetailView):
    model = Release

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from .custom import create_release_view_context

        create_release_view_context(context)

        return context


class ReleaseDownloadView(View):
    def get(self, request, pk):
        "Allow the user to download a release JSON file"

        cur_object = get_object_or_404(Release, pk=pk)
        file_data = cur_object.json_file
        file_data.open()
        data = file_data.read()
        resp = HttpResponse(
            data,
            content_type="application/json",
        )
        resp["Content-Disposition"] = 'attachment; filename="schema_{0}.json"'.format(
            cur_object.tag,
        )
        return resp


################################################################################
# REST API


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    permission_classes = [permissions.IsAdminUser]


class FormatSpecificationViewSet(viewsets.ModelViewSet):
    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]

    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ADMIN_ONLY_HTTP_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    queryset = FormatSpecification.objects.all()
    serializer_class = FormatSpecificationSerializer


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ADMIN_ONLY_HTTP_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, pk):
        ent = get_object_or_404(Entity, pk=pk)
        serializer = EntitySerializer(ent, context={"request": request})
        return Response(serializer.data)


class QuantityViewSet(viewsets.ModelViewSet):
    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ADMIN_ONLY_HTTP_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    queryset = Quantity.objects.all()
    serializer_class = QuantitySerializer


class DataFileViewSet(viewsets.ModelViewSet):
    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ADMIN_ONLY_HTTP_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    queryset = DataFile.objects.all()
    serializer_class = DataFileSerializer


class ReleasePagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 3


class ReleaseViewSet(viewsets.ModelViewSet):
    # Enable dots to be used in release tag names. See
    # https://stackoverflow.com/questions/27963899/django-rest-framework-using-dot-in-url

    authentication_classes = [
        instrumentdb.authentication.ExpiringTokenAuthentication,
        SessionAuthentication,
    ]
    pagination_class = ReleasePagination

    def get_permissions(self):
        if self.request.method in ADMIN_ONLY_HTTP_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    lookup_value_regex = "[\\w.]+"
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer


################################################################################


def navigate_tree_of_entities(url_components: List[str]) -> Entity:
    # Filter out empty components. (This can be the case if e.g. the
    # caller mistakenly writes two `/` characters, like in
    # `/tree/satellite//telescope/cad`.)
    url_components = [x for x in url_components if x != ""]

    matching_entries = Entity.objects.filter(name=url_components[0])

    # We are looking for a root node
    depth0_entry = None
    for cur_entry in matching_entries:
        if cur_entry.is_root_node():
            if depth0_entry is None:
                depth0_entry = cur_entry
            else:
                raise Http404(f"more than one root node with name {url_components[0]}")

    cur_obj = depth0_entry

    if len(url_components) == 1:
        return cur_obj

    try:
        for comp in url_components[1:-1]:
            cur_obj = cur_obj.get_children().get(name=comp)
    except (Entity.DoesNotExist, AttributeError):
        raise ValueError("Invalid path {}".format("/".join(url_components)))

    last_name = url_components[-1]
    if last_name.endswith("/"):
        last_name = last_name[:-1]

    if cur_obj is None:
        raise ValueError(
            "no matching item for path '{}'".format("/".join(url_components))
        )

    try:
        return cur_obj.quantities.get(name=last_name)
    except Quantity.DoesNotExist:
        matching_entries = Entity.objects.filter(name=last_name, parent=cur_obj)
        if len(matching_entries) == 0:
            raise Http404(
                f"No entity found with name {last_name} in URL {'/'.join(url_components)}"
            )
        if len(matching_entries) > 1:
            raise ValueError(
                f"More than one entry matched the name {last_name} "
                f"in the children of {cur_obj.name}"
            )

        return matching_entries[0]


def api_response_error(message: str, status: int) -> HttpResponse:
    return HttpResponse(json.dumps({"error": message}).encode("utf-8"), status=status)


def entity_reference_view(request, reference: str):
    """
    Access an entity through its path

    If `reference` is `/satellite/LFT`, the result of this
    function will be a redirect to the
    """
    try:
        cur_obj = navigate_tree_of_entities(url_components=reference.split("/"))
    except ValueError as err:
        return api_response_error(message=str(err), status=status.HTTP_400_BAD_REQUEST)
    except Http404 as err:
        return api_response_error(message=str(err), status=status.HTTP_400_BAD_REQUEST)

    if isinstance(cur_obj, Quantity):
        return redirect("quantity-detail", cur_obj.uuid)
    elif isinstance(cur_obj, Entity):
        return redirect("entity-detail", cur_obj.uuid)
    else:
        return api_response_error(
            message=f"invalid reference '{reference}'",
            status=status.HTTP_400_BAD_REQUEST,
        )


def release_view(request, rel_name: str, reference: str, browse_view=False):
    # If browse_view is True, redirect to browse/data_files/uuid
    # If browse_view is False, redirect to api/data_files/uuid

    release = get_object_or_404(Release, tag=rel_name)

    # The "reference" here is the part of the URL that includes the
    # list of entities and the quantity. For instance, if "reference"
    # is "mft/detectors/det0a/noise_properties", this is the meaning
    # of its parts:
    #
    #     mft / detectors / det0a / noise_properties
    #     |---------------------|   |--------------|
    #               ^                      ^
    #               |                      |
    #      sequence of entities         quantity

    url_components = reference.split("/")

    try:
        cur_obj = navigate_tree_of_entities(url_components=url_components[:-1])

        quantity_name = url_components[-1]
        quantity = get_object_or_404(cur_obj.quantities, name=quantity_name)
        data_file = get_object_or_404(
            quantity.data_files, release_tags__tag=release.tag
        )
    except ValueError as err:
        return api_response_error(message=str(err), status=status.HTTP_400_BAD_REQUEST)
    except Http404 as err:
        return api_response_error(message=str(err), status=status.HTTP_400_BAD_REQUEST)

    if browse_view:
        return redirect("data-file-view", data_file.uuid)
    else:
        return redirect("datafile-detail", data_file.uuid)


def api_release_view(request, rel_name, reference):
    return release_view(request, rel_name, reference, browse_view=False)


def browse_release_view(request, rel_name, reference):
    return release_view(request, rel_name, reference, browse_view=True)


@api_view(["POST"])
@permission_classes(
    (AllowAny,)
)  # here we specify permission by default we set IsAuthenticated
def login_request(request):
    login_serializer = UserSigninSerializer(
        data=request.data, context={"request": request}
    )
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(
        username=login_serializer.data["username"],
        password=login_serializer.data["password"],
    )
    if not user:
        return Response(
            {"detail": "Invalid Credentials or account not active"},
            status=HTTP_404_NOT_FOUND,
        )

    token, created = Token.objects.get_or_create(user=user)

    if not created and not is_token_expired(token):
        # update the created time of the token to keep it valid
        token.created = datetime.utcnow().replace(tzinfo=timezone.utc)
        token.save()

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)
    user_serialized = UserSerializer(user, context={"request": request})

    groups_array = []
    for key in list(user.groups.values()):
        groups_array.append(key["name"])

    return Response(
        {
            "user": user_serialized.data["username"],
            "groups:": groups_array,
            "token": token.key,
            "token_expires_in_minutes": int(
                ceil(expires_in(token).total_seconds()) // 60
            ),
        },
        status=HTTP_200_OK,
    )
