# -*- encoding: utf-8 -*-
import json
from io import StringIO
from uuid import UUID

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from browse.models import (
    FormatSpecification,
    Entity,
    Quantity,
    DataFile,
    Release,
)
from django.contrib.auth.models import User

from browse.views import DataFileViewSet

TEST_ACCOUNT_EMAIL = "test@localhost"
TEST_ACCOUNT_USER = "test_user"

TEST_ACCOUNT_ADMIN_EMAIL = "admin@localhost"
TEST_ACCOUNT_ADMIN_USER = "test_admin"


def _create_test_user_and_authenticate(client, superuser: bool):
    if superuser:
        test_user = User.objects.create_superuser(
            email=TEST_ACCOUNT_ADMIN_EMAIL, username=TEST_ACCOUNT_ADMIN_USER
        )
    else:
        test_user = User.objects.create_user(
            email=TEST_ACCOUNT_EMAIL, username=TEST_ACCOUNT_USER
        )

    client.force_authenticate(user=test_user)
    return test_user


def create_format_spec(client, document_ref):
    "Create a FormatSpecification object and return the response"

    url = reverse("formatspecification-list")

    format_spec_file = StringIO("Test file")

    response = client.post(
        url,
        data={
            "document_ref": document_ref,
            "title": "My dummy document",
            "file_mime_type": "application/text",
            "doc_file": format_spec_file,
        },
    )
    return response


def create_entity_spec(client, name, parent=None):
    "Create a Entity object and return the response"

    url = reverse("entity-list")

    response = client.post(
        url, format="json", data={"name": name, "parent": parent, "quantities": []}
    )
    return response


def create_quantity_spec(client, name, entity, format_spec, data_files=[]):
    "Create a Quantity object and return the response"

    url = reverse("quantity-list")

    response = client.post(
        url,
        data={
            "name": name,
            "parent_entity": entity,
            "format_spec": format_spec,
            "data_files": data_files,
        },
    )
    return response


def create_data_file_spec(
    client, name, metadata, quantity, spec_version="1.0", release_tags=[]
):
    "Create a DataFile object and return the response"

    url = reverse("datafile-list")

    data_file = StringIO("1,2,3,4,5")

    # Since we are sending "file_data", we cannot use
    # format="json" here. Because of this, we need to
    # manually convert `metadata` into a string, otherwise
    # the `post` method would not be able to send both
    # the metadata (a nested structure) and the file data.
    response = client.post(
        url,
        data={
            "name": name,
            "metadata": metadata if isinstance(metadata, str) else json.dumps(metadata),
            "quantity": quantity,
            "spec_version": spec_version,
            "release_tags": release_tags,
            "file_data": data_file,
        },
    )
    return response


def create_release_spec(client, tag, comment="", data_files=[]):
    "Create a Release object and return the response"

    url = reverse("release-list")

    from io import StringIO

    release_document = StringIO("Contents of the release document")
    release_document.name = "reldoc.txt"

    response = client.post(
        url,
        data={
            "tag": tag,
            "comment": comment,
            "data_files": data_files,
            "release_document_mime_type": "text/plain",
            "release_document": release_document,
        },
    )

    return response


class FormatSpecificationTests(APITestCase):
    def setUp(self) -> None:
        self.user = _create_test_user_and_authenticate(
            client=self.client, superuser=True
        )

    def test_create_format_spec(self):
        """
        Ensure we can create a new FormatSpecification object.
        """

        response = create_format_spec(self.client, "DUMMY_REF_001")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormatSpecification.objects.count(), 1)
        self.assertEqual(
            FormatSpecification.objects.get().document_ref, "DUMMY_REF_001"
        )

    def test_download_format_specification(self):
        """
        Ensure we can create a new DataFile object.
        """
        response = create_format_spec(self.client, "DUMMY_REF_001")

        # Now ask for a JSON representation of the object
        json_dict = self.client.get(response.data["url"]).json()

        response = self.client.get(json_dict["download_link"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")

        expected_content = b"Test file"
        actual_content = b"".join(chunk for chunk in response.streaming_content)
        self.assertEqual(actual_content, expected_content)


class EntityTests(APITestCase):
    def setUp(self) -> None:
        self.user = _create_test_user_and_authenticate(
            client=self.client, superuser=True
        )

    def test_create_entity(self):
        """
        Ensure we can create a new quantity object.
        """

        response = create_entity_spec(self.client, "test_entity")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.get().name, "test_entity")

        response = self.client.get("/tree/test_entity/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Since we got HTTP 302, this is a redirect and we must follow the alias
        response = self.client.get(response.url)
        entity_json = response.json()
        self.assertEqual(UUID(entity_json["uuid"]), Entity.objects.get().uuid)

    def test_entities_with_same_name(self):
        response = create_entity_spec(self.client, "entity")
        response = create_entity_spec(
            self.client, "entity", parent=response.data["url"]
        )
        response = create_entity_spec(
            self.client, "entity", parent=response.data["url"]
        )

        # This is the URL of the entity `entity/entity/entity`
        url = response.data["url"]

        response = self.client.get("/tree/entity/entity/entity/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Follow the redirect
        response = self.client.get(response.url)
        self.assertEqual(response.data["url"], url)

    def test_entities_with_name_clashes(self):
        response = create_entity_spec(self.client, "entity")
        parent_url = response.data["url"]

        # Two children with the same name
        response = create_entity_spec(self.client, "subentity", parent=parent_url)
        response = create_entity_spec(self.client, "subentity", parent=parent_url)

        # Make an ambiguous call
        response = self.client.get("/tree/entity/subentity/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nested_entities(self):
        parent_entity = create_entity_spec(self.client, "test_entity").json()
        child_entity = create_entity_spec(
            self.client, "child1", parent=parent_entity["url"]
        ).json()
        sub_child_entity = create_entity_spec(
            self.client, "child2", parent=child_entity["url"]
        ).json()

        response = self.client.get("/tree/test_entity/child1/child2/")
        # HTTP 302 marks a redirection
        self.assertEqual(response.status_code, 302)

        # Get the true entity
        response = self.client.get(response.url)
        self.assertEqual(response.json()["url"], sub_child_entity["url"])

    def test_look_for_nonexistent_quantity(self):
        response = self.client.get("/tree/this_entity_does_not_exist")
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


class QuantityTests(APITestCase):
    def setUp(self):
        self.user = _create_test_user_and_authenticate(
            client=self.client, superuser=True
        )

        self.formatspec_response = create_format_spec(self.client, "DUMMY_REF_001")
        self.assertEqual(self.formatspec_response.status_code, status.HTTP_201_CREATED)

        self.entity_response = create_entity_spec(self.client, "test_entity")
        self.assertEqual(self.entity_response.status_code, status.HTTP_201_CREATED)

    def test_create_quantity(self):
        """
        Ensure we can create a new quantity object.
        """

        response = create_quantity_spec(
            self.client,
            name="test_quantity",
            entity=self.entity_response.data["url"],
            format_spec=self.formatspec_response.data["url"],
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quantity.objects.count(), 1)
        self.assertEqual(Quantity.objects.get().name, "test_quantity")

        response = self.client.get("/tree/test_entity/test_quantity/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Since we got HTTP 302, this is a redirect and we must follow the alias
        response = self.client.get(response.url)
        quantity_json = response.json()
        self.assertEqual(UUID(quantity_json["uuid"]), Quantity.objects.get().uuid)

    def test_look_for_nonexistent_quantity(self):
        response = self.client.get("/tree/test_entity/this_does_not_exist")
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


class DataFileTests(APITestCase):
    def setUp(self):
        self.user = _create_test_user_and_authenticate(
            client=self.client, superuser=True
        )

        self.formatspec_response = create_format_spec(self.client, "DUMMY_REF_001")
        self.assertEqual(self.formatspec_response.status_code, status.HTTP_201_CREATED)

        self.entity_response = create_entity_spec(self.client, "test_entity")
        self.assertEqual(self.entity_response.status_code, status.HTTP_201_CREATED)

        self.quantity_response = create_quantity_spec(
            self.client,
            name="test_quantity",
            entity=self.entity_response.data["url"],
            format_spec=self.formatspec_response.data["url"],
        )
        self.assertEqual(self.quantity_response.status_code, status.HTTP_201_CREATED)

    def test_create_datafile(self):
        """
        Ensure we can create a new DataFile object.
        """
        response = create_data_file_spec(
            self.client,
            name="test_datafile",
            metadata={"a": 10, "b": "hello"},
            quantity=self.quantity_response.data["url"],
        )

        # Check the result of the POST call
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DataFile.objects.count(), 1)

        data_file_obj = DataFile.objects.get()
        self.assertEqual(data_file_obj.name, "test_datafile")
        self.assertEqual(
            data_file_obj.full_path, "test_entity/test_quantity/test_datafile"
        )

        # Now get the object from the database and check that
        # everything looks ok
        response = self.client.get(response.data["url"])
        json = response.json()

        assert "quantity" in json
        self.assertEqual(json["quantity"], self.quantity_response.data["url"])

        assert "metadata" in json
        self.assertEqual(json["metadata"]["a"], 10)
        self.assertEqual(json["metadata"]["b"], "hello")

    def test_create_datafile_with_wrong_metadata(self):
        """
        Ensure we can create a new DataFile object.
        """
        response = create_data_file_spec(
            self.client,
            name="test_datafile",
            metadata="a b",  # This is invalid JSON!
            quantity=self.quantity_response.data["url"],
        )

        # Check the result of the POST call
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_datafile(self):
        """
        Ensure we can create a new DataFile object.
        """
        response = create_data_file_spec(
            self.client,
            name="test_datafile",
            metadata={"a": 10, "b": "hello"},
            quantity=self.quantity_response.data["url"],
        )

        # Now ask for a JSON representation of the object
        json = self.client.get(response.data["url"]).json()

        response = self.client.get(json["download_link"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/text")

        expected_content = b"1,2,3,4,5"
        actual_content = b"".join(chunk for chunk in response.streaming_content)
        self.assertEqual(actual_content, expected_content)


class ReleaseTests(APITestCase):
    def setUp(self):
        self.user = _create_test_user_and_authenticate(
            client=self.client, superuser=True
        )

        self.formatspec_response = create_format_spec(self.client, "DUMMY_REF_001")
        self.entity_response = create_entity_spec(self.client, "test_entity")
        self.quantity_response = create_quantity_spec(
            self.client,
            name="test_quantity",
            entity=self.entity_response.data["url"],
            format_spec=self.formatspec_response.data["url"],
        )
        self.datafile_response = create_data_file_spec(
            self.client,
            name="test_datafile",
            metadata={"a": 10, "b": "hello"},
            quantity=self.quantity_response.data["url"],
        )

    def test_create_release(self):
        """
        Ensure we can create a new Release object.
        """
        self.client.force_login(self.user)

        response = create_release_spec(self.client, "v1.0")

        # Check the result of the POST call
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Release.objects.count(), 1)
        self.assertEqual(Release.objects.get().tag, "v1.0")

        # Add a datafile to the release
        rel_url = response.data["url"]
        response = self.client.patch(
            rel_url,
            format="json",
            data={
                "tag": "v1.0",
                "comment": "",
                "data_files": [self.datafile_response.data["url"]],
            },
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(rel_url)
        json = response.json()
        self.assertEqual(json["tag"], "v1.0")
        self.assertEqual(len(json["data_files"]), 1)
        self.assertEqual(json["release_document_mime_type"], "text/plain")
        self.assertTrue(json["release_document"] is not None)

        # Try to access the data file through the release tag
        response = self.client.get(
            "/releases/v1.0/test_entity/test_quantity/", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        assert response.url in self.datafile_response.data["url"]

        # Download the release document

        response = self.client.get("/browse/releases/v1.0/document/", follow=True)
        self.assertEqual(response.content, b"Contents of the release document")


class AuthenticateTest(APITestCase):
    def setUp(self) -> None:
        # This user has superpowers, because we need to populate the database
        _create_test_user_and_authenticate(client=self.client, superuser=True)

        self.formatspec_response = create_format_spec(self.client, "DUMMY_REF_001")
        self.entity_response = create_entity_spec(self.client, "test_entity")
        self.quantity_response = create_quantity_spec(
            self.client,
            name="test_quantity",
            entity=self.entity_response.data["url"],
            format_spec=self.formatspec_response.data["url"],
        )
        self.datafile_response = create_data_file_spec(
            self.client,
            name="test_datafile",
            metadata={"a": 10, "b": "hello"},
            quantity=self.quantity_response.data["url"],
        )

        # This user has no superpowers, and it's what we're going to use in the
        # tests
        _create_test_user_and_authenticate(client=self.client, superuser=False)

    def testDenyCreationOfFormatSpec(self):
        response = create_format_spec(
            client=self.client, document_ref="ThisShouldTriggerAnError"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testDenyCreationOfEntity(self):
        response = create_entity_spec(
            client=self.client, name="ThisShouldTriggerAnError", parent=None
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testDenyCreationOfQuantity(self):
        response = create_quantity_spec(
            client=self.client,
            name="ThisShouldTriggerAnError",
            entity=self.entity_response.data["url"],
            format_spec=self.formatspec_response.data["url"],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testDenyCreationOfDataFile(self):
        response = create_data_file_spec(
            client=self.client,
            name="ThisShouldTriggerAnError",
            metadata="",
            quantity=self.quantity_response.data["url"],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


def test_unauthenticated_access(self):
    view = DataFileViewSet.as_view({"get": "list"})
    factory = APIRequestFactory()
    request = factory.get("/data-files/")

    response = view(request)
    self.assertEqual(response.status_code, 401)  # Assert unauthorized access
