# -*- encoding: utf-8 -*-

import datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from browse.models import Entity, FormatSpecification, Quantity, DataFile, Release


def get_white_test_image(name: str = "test_image.gif") -> SimpleUploadedFile:
    # Taken from https://stackoverflow.com/a/50453780/3967151
    small_gif = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
        b"\x02\x4c\x01\x00\x3b"
    )
    return SimpleUploadedFile(name, small_gif, content_type="image/gif")


def get_black_test_image(name: str = "test_image.gif") -> SimpleUploadedFile:
    # Taken from https://stackoverflow.com/a/50453780/3967151
    small_gif = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04"
        b"\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44"
        b"\x01\x00\x3b"
    )
    return SimpleUploadedFile(name, small_gif, content_type="image/gif")


class TextExport(TestCase):
    def setUp(self):
        # Fill the test database
        self.fmt_spec = FormatSpecification(
            document_ref="REF001",
            title="Document 001",
            doc_file=SimpleUploadedFile(
                name="REF001.txt", content=b"Format specification"
            ),
            doc_file_name="REF001.txt",
            doc_mime_type="text/plain",
            file_mime_type="text/json",
        )
        self.fmt_spec.save()

        # The tree of entities will have this shape:
        #
        # root
        # |
        # +--- child1
        # |    |
        # |    +--- subchild1
        # |
        # +--- child2
        #      |
        #      +--- subchild2
        #      |
        #      +--- subchild3

        self.entity_root = Entity(
            name="root",
            parent=None,
        )
        self.entity_root.save()

        self.entity_child1 = Entity(
            name="child1",
            parent=self.entity_root,
        )
        self.entity_child1.save()

        self.entity_child2 = Entity(
            name="child2",
            parent=self.entity_root,
        )
        self.entity_child2.save()

        self.entity_subchild1 = Entity(
            name="subchild1",
            parent=self.entity_child1,
        )
        self.entity_subchild1.save()

        self.entity_subchild2 = Entity(
            name="subchild2",
            parent=self.entity_child2,
        )
        self.entity_subchild2.save()

        self.entity_subchild3 = Entity(
            name="subchild3",
            parent=self.entity_child2,
        )
        self.entity_subchild3.save()

        # Add one quantity to subchild1 and to subchild2
        self.quantity_subchild1 = Quantity(
            name="subchild1_quantity",
            format_spec=self.fmt_spec,
            parent_entity=self.entity_subchild1,
        )
        self.quantity_subchild1.save()

        self.quantity_subchild2 = Quantity(
            name="subchild2_quantity",
            format_spec=self.fmt_spec,
            parent_entity=self.entity_subchild2,
        )
        self.quantity_subchild2.save()

        # Add two data files to each of the two quantities, and mark a
        # dependence between them

        self.subchild1_file1 = DataFile(
            name="subchild1_file1",
            upload_date="2023-01-02T03:04:05",
            metadata='{"subchild1_metadata_field": 1}',
            file_data=SimpleUploadedFile(
                name="datafile1.json",
                content=b'{"subchild1_file_field": 2}',
            ),
            quantity=self.quantity_subchild1,
            spec_version="v1.0",
            plot_file=get_white_test_image(),
            plot_mime_type="image/gif",
            comment="Oldest data file for subchild1",
        )
        self.subchild1_file1.save()

        self.subchild1_file2 = DataFile(
            name="subchild1_file2",
            upload_date="2023-01-02T03:04:05",
            metadata='{"subchild1_metadata_field": 2}',
            file_data=SimpleUploadedFile(
                name="datafile1.json",
                content=b'{"subchild1_file_field": 3}',
            ),
            quantity=self.quantity_subchild1,
            spec_version="v1.1",
            plot_file=get_black_test_image(),
            plot_mime_type="image/gif",
            comment="Newest data file for subchild1",
        )
        self.subchild1_file2.save()

        self.subchild2_file1 = DataFile(
            name="subchild2_file1",
            upload_date="2023-01-02T03:04:05",
            metadata='{"subchild2_metadata_field": 1}',
            file_data=SimpleUploadedFile(
                name="datafile1.json", content=b'{"subchild2_file_field": 4}'
            ),
            quantity=self.quantity_subchild2,
            spec_version="v1.0",
            plot_file=get_white_test_image(),
            plot_mime_type="image/gif",
            comment="Oldest data file for subchild2",
        )
        self.subchild2_file1.dependencies.add(self.subchild1_file1)
        self.subchild2_file1.save()

        self.subchild2_file2 = DataFile(
            name="subchild2_file2",
            upload_date="2023-01-02T03:04:05",
            metadata='{"subchild2_metadata_field": 2}',
            file_data=SimpleUploadedFile(
                name="datafile1.json", content=b'{"subchild2_file_field": 5}'
            ),
            quantity=self.quantity_subchild2,
            spec_version="v1.1",
            plot_file=get_black_test_image(),
            plot_mime_type="image/gif",
            comment="Newest data file for subchild2",
        )
        self.subchild2_file2.dependencies.add(self.subchild1_file2)
        self.subchild2_file2.save()

        # Finally, create *two* releases

        self.release1 = Release(
            tag="v1.2345",
            rel_date="2023-05-07T05:06:07",
            comment="Release comment 1",
            release_document=SimpleUploadedFile(
                name="reldoc.txt", content=b"Release document 1"
            ),
            release_document_mime_type="text/plain",
        )
        self.release1.save()

        for cur_file in [self.subchild1_file1, self.subchild2_file1]:
            cur_file.release_tags.add(self.release1)
            cur_file.save()

        self.release2 = Release(
            tag="v2.3456",
            rel_date="2023-05-08T05:06:07",
            comment="Release comment 2",
            release_document=SimpleUploadedFile(
                name="reldoc.txt", content=b"Release document 2"
            ),
            release_document_mime_type="text/plain",
        )
        self.release2.save()

        for cur_file in [self.subchild1_file2, self.subchild2_file2]:
            cur_file.release_tags.add(self.release2)
            cur_file.save()

    def test_export_everything(self):
        with TemporaryDirectory() as tempdir:
            dest_path = Path(tempdir) / "output"
            call_command("export", dest_path)

            # Check that the JSON file was saved

            schema_file = dest_path / "schema.json"
            self.assertTrue(schema_file.exists())

            # Check that the format specifications were saved

            format_spec_path = dest_path / "format_spec"
            self.assertTrue(format_spec_path.exists())

            format_spec_file = format_spec_path / f"{self.fmt_spec.uuid}_REF001.txt"
            self.assertTrue(format_spec_file.exists())

            with format_spec_file.open("rt") as inpf:
                contents = "".join(inpf.readlines()).strip()
                self.assertEqual(contents, "Format specification")

            # Check that the data files and plots were saved

            data_file_path = dest_path / "data_files"
            self.assertTrue(data_file_path.exists())

            plot_file_path = dest_path / "plot_files"
            self.assertTrue(plot_file_path)

            for cur_data_file, key, value, dependency in [
                (self.subchild1_file1, "subchild1_file_field", 2, None),
                (self.subchild1_file2, "subchild1_file_field", 3, None),
                (self.subchild2_file1, "subchild2_file_field", 4, self.subchild1_file1),
                (self.subchild2_file2, "subchild2_file_field", 5, self.subchild1_file2),
            ]:
                # First check the data files…

                cur_data_file_path = (
                    data_file_path / f"{cur_data_file.uuid}_{cur_data_file.name}"
                )
                self.assertTrue(cur_data_file_path.exists())

                with cur_data_file_path.open("rt") as inpf:
                    cur_file_contents = json.load(inpf)
                    self.assertEqual(cur_file_contents[key], value)

                if not dependency:
                    self.assertEqual(len(cur_data_file.dependencies.all()), 0)
                else:
                    self.assertEqual(len(cur_data_file.dependencies.all()), 1)
                    # This call will fail if there is no match or more than one match
                    _ = cur_data_file.dependencies.get(name=dependency.name)

                # …and then the plot files

                cur_plot_file = dest_path / cur_data_file.plot_file.name
                self.assertTrue(cur_plot_file.exists())

            # Finally, check that all the release documents were exported
            release_path = dest_path / "release_documents"
            self.assertTrue(release_path.exists())

            release1_doc = release_path / "v1.2345.txt"
            self.assertTrue(release1_doc.exists())
            with release1_doc.open("rt") as inpf:
                self.assertEqual(
                    "".join(inpf.readlines()).strip(), "Release document 1"
                )

            release2_doc = release_path / "v2.3456.txt"
            self.assertTrue(release2_doc.exists())
            with release2_doc.open("rt") as inpf:
                self.assertEqual(
                    "".join(inpf.readlines()).strip(), "Release document 2"
                )

    def test_export_and_import(self):
        with TemporaryDirectory() as tempdir:
            export_path = Path(tempdir) / "test"

            # Step 1: export the database
            call_command("export", export_path)

            # Step 2: delete everything from the database
            DataFile.objects.all().delete()
            Quantity.objects.all().delete()
            Entity.objects.all().delete()
            FormatSpecification.objects.all().delete()
            Release.objects.all().delete()

            # Step 3: import the files from the export path
            call_command("import", export_path / "schema.json")

            # Step 4: check that the database was rebuilt correctly

            #     Check that all the objects were rebuilt
            self.assertEqual(len(DataFile.objects.all()), 4)
            self.assertEqual(len(Quantity.objects.all()), 2)
            self.assertEqual(len(Entity.objects.all()), 6)
            self.assertEqual(len(Release.objects.all()), 2)
            self.assertEqual(len(FormatSpecification.objects.all()), 1)

            #     Check that the format specification is correct
            fmt_spec = FormatSpecification.objects.filter(document_ref="REF001")
            self.assertEqual(len(fmt_spec), 1)
            fmt_spec = fmt_spec[0]
            self.assertEqual(fmt_spec.title, "Document 001")
            self.assertEqual(fmt_spec.doc_mime_type, "text/plain")
            self.assertEqual(fmt_spec.file_mime_type, "text/json")

            fmt_spec.doc_file.open()
            self.assertEqual(fmt_spec.doc_file.read(), b"Format specification")

            #     Check that the tree of entities is correct
            entity_root = Entity.objects.get(name="root")
            self.assertEqual(entity_root.parent, None)

            entity_child1 = Entity.objects.get(name="child1")
            self.assertEqual(entity_child1.parent, entity_root)

            entity_child2 = Entity.objects.get(name="child2")
            self.assertEqual(entity_child2.parent, entity_root)

            entity_subchild1 = Entity.objects.get(name="subchild1")
            self.assertEqual(entity_subchild1.parent, entity_child1)

            entity_subchild2 = Entity.objects.get(name="subchild2")
            self.assertEqual(entity_subchild2.parent, entity_child2)

            entity_subchild3 = Entity.objects.get(name="subchild3")
            self.assertEqual(entity_subchild3.parent, entity_child2)

            #     Check that the quantities are correct
            quantity_subchild1 = Quantity.objects.get(name="subchild1_quantity")
            self.assertEqual(quantity_subchild1.format_spec.uuid, fmt_spec.uuid)
            self.assertEqual(
                quantity_subchild1.parent_entity.uuid, entity_subchild1.uuid
            )

            quantity_subchild2 = Quantity.objects.get(name="subchild2_quantity")
            self.assertEqual(quantity_subchild2.format_spec.uuid, fmt_spec.uuid)
            self.assertEqual(
                quantity_subchild2.parent_entity.uuid, entity_subchild2.uuid
            )

            #     Check that the data files are correct
            for (
                cur_file_name,
                cur_metadata_key,
                cur_metadata_val,
                cur_file_key,
                cur_file_val,
                cur_quantity,
            ) in [
                (
                    "subchild1_file1",
                    "subchild1_metadata_field",
                    1,
                    "subchild1_file_field",
                    2,
                    quantity_subchild1,
                ),
                (
                    "subchild1_file2",
                    "subchild1_metadata_field",
                    2,
                    "subchild1_file_field",
                    3,
                    quantity_subchild1,
                ),
                (
                    "subchild2_file1",
                    "subchild2_metadata_field",
                    1,
                    "subchild2_file_field",
                    4,
                    quantity_subchild2,
                ),
                (
                    "subchild2_file2",
                    "subchild2_metadata_field",
                    2,
                    "subchild2_file_field",
                    5,
                    quantity_subchild2,
                ),
            ]:
                cur_file = DataFile.objects.get(name=cur_file_name)
                self.assertEqual(
                    cur_file.upload_date,
                    datetime.datetime(
                        2023, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc
                    ),
                )

                cur_file_metadata = json.loads(cur_file.metadata)
                self.assertEqual(
                    cur_file_metadata[cur_metadata_key],
                    cur_metadata_val,
                )

                self.assertTrue(cur_file.file_data is not None)
                cur_file.file_data.open()
                cur_file_data = json.loads(cur_file.file_data.read().decode("utf-8"))
                self.assertEqual(cur_file_data[cur_file_key], cur_file_val)

                self.assertEqual(cur_file.quantity.uuid, cur_quantity.uuid)

                self.assertTrue(cur_file.plot_file is not None)
                self.assertEqual(cur_file.plot_mime_type, "image/gif")

            #     Check that the releases are correct
            for (
                cur_release_tag,
                cur_release_comment,
                cur_release_document,
                cur_release_day,
            ) in [
                ("v1.2345", "Release comment 1", b"Release document 1", 7),
                ("v2.3456", "Release comment 2", b"Release document 2", 8),
            ]:
                cur_rel = Release.objects.get(tag=cur_release_tag)
                self.assertEqual(
                    cur_rel.rel_date,
                    datetime.datetime(
                        2023, 5, cur_release_day, 5, 6, 7, tzinfo=datetime.timezone.utc
                    ),
                )
                self.assertEqual(cur_rel.comment, cur_release_comment)
                self.assertTrue(cur_rel.release_document is not None)
                cur_rel.release_document.open()
                self.assertEqual(cur_rel.release_document.read(), cur_release_document)
                self.assertEqual(cur_rel.release_document_mime_type, "text/plain")
