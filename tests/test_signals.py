# -*- encoding: utf-8 -*-

import json
from django.test import TestCase
from browse.models import (
    Entity,
    Quantity,
    DataFile,
    Release,
    FormatSpecification,
    dump_db_to_json,
    ReleaseDumpConfiguration,
    DumpOutputFormat,
)
from pathlib import Path
from tempfile import TemporaryDirectory


class ReleaseSignalTestCase(TestCase):
    def setUp(self):
        self.spec = FormatSpecification.objects.create(
            document_ref="SPEC-001",
            title="Test Spec",
            file_mime_type="application/json",
        )
        self.entity = Entity.objects.create(name="base_instrument")
        self.quantity = Quantity.objects.create(
            name="my_quantity",
            format_spec=self.spec,
            parent_entity=self.entity,
        )
        self.datafile = DataFile.objects.create(
            name="calib_data.json",
            quantity=self.quantity,
            spec_version="1.0",
            metadata='{"gain": 1.2}',
        )

    def test_automatic_json_generation_on_m2m_update(self):
        """
        Verify that adding a DataFile to a Release triggers a JSON
        regeneration that includes the file.
        """
        # This should trigger the initial save
        rel = Release.objects.create(tag="v1.0-test", comment="Testing signals")

        # This should trigger the `m2m_changed` signal
        rel.data_files.add(self.datafile)

        rel.refresh_from_db()

        self.assertTrue(bool(rel.json_file), "The Release.json_file field is empty.")

        with rel.json_file.open("r") as f:
            schema_data = json.load(f)

        df_uuids = [df["uuid"] for df in schema_data.get("data_files", [])]
        self.assertIn(
            str(self.datafile.uuid),
            df_uuids,
            "DataFile was missing from the JSON dump.",
        )

    def test_export_command_with_release_tag(self):
        """
        Verify that dump_db_to_json correctly filters files when
        a release_tag is provided.
        """
        rel = Release.objects.create(tag="v2.0-target")
        rel.data_files.add(self.datafile)

        with TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            cfg = ReleaseDumpConfiguration(
                no_attachments=True,
                only_tree=False,
                exist_ok=True,
                skip_empty_entities=False,
                skip_empty_quantities=False,
                output_format=DumpOutputFormat.JSON,
                output_folder=temp_path,
            )

            # Call the dump function for this specific tag
            json_path = dump_db_to_json(cfg, release_tag="v2.0-target")

            with open(json_path, "r") as f:
                exported_data = json.load(f)

            # The 'data_files' section should contain our linked file
            self.assertEqual(len(exported_data["data_files"]), 1)
            self.assertEqual(
                exported_data["data_files"][0]["uuid"], str(self.datafile.uuid)
            )
