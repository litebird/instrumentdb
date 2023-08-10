# -*- encoding: utf-8 -*-

import json

from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.models import User, Group
from browse.models import (
    Entity,
    Quantity,
    DataFile,
    FormatSpecification,
    Release,
    validate_json,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class FormatSpecificationSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="formatspecification-detail", read_only=True
    )

    class Meta:
        model = FormatSpecification
        fields = [
            "uuid",
            "url",
            "document_ref",
            "title",
            "doc_file",
            "doc_file_name",
            "doc_mime_type",
            "file_mime_type",
        ]
        extra_kwargs = {
            "doc_file": {
                "max_length": 512,
            }
        }

    def to_representation(self, instance):
        representation = super(FormatSpecificationSerializer, self).to_representation(
            instance
        )
        representation["download_link"] = reverse(
            "format-spec-download-view",
            kwargs={"pk": instance.uuid},
            request=self.context["request"],
        )

        return representation


class SubEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "uuid",
            "name",
        ]


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    children = SubEntitySerializer(many=True, required=False)
    url = serializers.HyperlinkedIdentityField(
        view_name="entity-detail", read_only=True
    )

    class Meta:
        model = Entity
        fields = [
            "uuid",
            "url",
            "name",
            "parent",
            "children",
            "quantities",
        ]


class QuantitySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="quantity-detail", read_only=True
    )

    class Meta:
        model = Quantity
        fields = [
            "uuid",
            "url",
            "name",
            "format_spec",
            "parent_entity",
            "data_files",
        ]


def serializer_validate_json(value) -> None:
    from django.core.exceptions import ValidationError

    try:
        validate_json(value)
    except ValidationError as err:
        raise serializers.ValidationError(detail=err.message, code=err.code)


class JSONField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, str):
            # Validate the JSON and discard the result of the conversion
            result = json.loads(value)
        else:
            result = value

        return result

    def to_internal_value(self, data):
        if isinstance(data, dict):
            result = json.dumps(data)
        else:
            result = data

        return result


class DataFileSerializer(serializers.HyperlinkedModelSerializer):
    release_tags = serializers.HyperlinkedRelatedField(
        view_name="release-detail",
        many=True,
        queryset=Release.objects.all(),
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="datafile-detail", read_only=True
    )
    metadata = JSONField(validators=[serializer_validate_json])

    class Meta:
        model = DataFile
        fields = [
            "uuid",
            "url",
            "name",
            "upload_date",
            "file_data",
            "metadata",
            "quantity",
            "spec_version",
            "dependencies",
            "plot_mime_type",
            "plot_file",
            "comment",
            "release_tags",
        ]
        extra_kwargs = {
            "file_data": {
                "max_length": 512,
                "allow_empty_file": True,
            },
            "plot_file": {
                "max_length": 512,
                "allow_empty_file": True,
            },
        }

    def to_representation(self, instance):
        representation = super(DataFileSerializer, self).to_representation(instance)

        representation["download_link"] = reverse(
            "data-file-download-view",
            kwargs={"pk": instance.uuid},
            request=self.context["request"],
        )
        representation["plot_download_link"] = reverse(
            "data-file-plot-view",
            kwargs={"pk": instance.uuid},
            request=self.context["request"],
        )

        return representation


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    data_files = serializers.HyperlinkedRelatedField(
        view_name="datafile-detail",
        many=True,
        queryset=DataFile.objects.all(),
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="release-detail", read_only=True
    )
    release_document_url = serializers.HyperlinkedRelatedField(
        view_name="release-document-download-view", read_only=True
    )

    class Meta:
        model = Release
        fields = [
            "tag",
            "url",
            "rel_date",
            "comment",
            "release_document",
            "release_document_mime_type",
            "release_document_url",
            "data_files",
        ]
        extra_kwargs = {
            "release_document": {
                "max_length": 512,
                "allow_empty_file": True,
            },
        }
        ordering = ["-rel_date"]

    def to_representation(self, instance):
        representation = super(ReleaseSerializer, self).to_representation(instance)

        representation["json_dump"] = reverse(
            "release-download-view",
            kwargs={"pk": instance.tag},
            request=self.context["request"],
        )

        return representation


class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
