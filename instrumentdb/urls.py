"""instrumentdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path

from rest_framework import routers

from browse.forms import change_password
from browse.views import (
    DataFileView,
    DataFilePlotDownloadView,
    DataFileDownloadView,
    entity_tree_view,
    EntityView,
    FormatSpecificationListView,
    FormatSpecificationDownloadView,
    QuantityView,
    ReleaseListView,
    ReleaseView,
    UserViewSet,
    GroupViewSet,
    FormatSpecificationViewSet,
    EntityViewSet,
    QuantityViewSet,
    DataFileViewSet,
    ReleaseViewSet,
    api_release_view,
    browse_release_view,
    login_request,
    ReleaseDownloadView,
    UserView,
)

################################################################################

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"format_specs", FormatSpecificationViewSet)
router.register(r"entities", EntityViewSet)
router.register(r"quantities", QuantityViewSet)
router.register(r"data_files", DataFileViewSet)
router.register(r"releases", ReleaseViewSet)

urlpatterns = [
    path("", ReleaseListView.as_view(), name="release-list-view"),
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("browse/data_files/<pk>/", DataFileView.as_view(), name="data-file-view"),
    path(
        "browse/data_files/<pk>/download/",
        DataFileDownloadView.as_view(),
        name="data-file-download-view",
    ),
    path(
        "browse/data_files/<pk>/plot/",
        DataFilePlotDownloadView.as_view(),
        name="data-file-plot-view",
    ),
    path("entities/", entity_tree_view, name="entity-list-view"),
    path("users/<username>/", UserView.as_view(), name="user-view"),
    path("changepassword/", change_password, name="user-change-password"),
    path("browse/entities/<pk>/", EntityView.as_view(), name="entity-view"),
    path("browse/quantities/<pk>/", QuantityView.as_view(), name="quantity-view"),
    path("browse/releases/<pk>/", ReleaseView.as_view(), name="release-view"),
    path(
        "browse/releases/<pk>/download/",
        ReleaseDownloadView.as_view(),
        name="release-download-view",
    ),
    path(
        "browse/format_specs/",
        FormatSpecificationListView.as_view(),
        name="format-spec-list-view",
    ),
    path(
        "browse/format_specs/<pk>/download/",
        FormatSpecificationDownloadView.as_view(),
        name="format-spec-download-view",
    ),
    re_path(
        r"^releases/(?P<rel_name>[\w.-]+)/(?P<reference>[\w./-]+)/$", api_release_view
    ),
    re_path(
        r"^browse/releases/(?P<rel_name>[\w.-]+)/(?P<reference>[\w./-]+)/$",
        browse_release_view,
    ),
    path("api/login", login_request),
    path("accounts/", include("django.contrib.auth.urls")),
]
