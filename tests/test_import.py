# -*- encoding: utf-8 -*-

from pathlib import Path
from django.core.management import call_command
from django.test import TestCase
from browse.models import Entity, FormatSpecification, Quantity, DataFile, Release


def check_db_size(
    test, entity_len, format_spec_len, quantity_len, data_file_len, release_len
):
    test.assertEqual(len(Entity.objects.all()), entity_len)
    test.assertEqual(len(FormatSpecification.objects.all()), format_spec_len)
    test.assertEqual(len(Quantity.objects.all()), quantity_len)
    test.assertEqual(len(DataFile.objects.all()), data_file_len)
    test.assertEqual(len(Release.objects.all()), release_len)


def check_deps_in_schema(test):
    horn01_synth_obj = DataFile.objects.get(uuid="37bb70e4-29b2-4657-ba0b-4ccefbc5ae36")
    horn01_grasp_obj = DataFile.objects.get(uuid="a6dd07ee-9721-4453-abb1-e58aa53a9c01")

    test.assertTrue(
        horn01_synth_obj.dependencies.filter(uuid=horn01_grasp_obj.uuid).exists()
    )


class TestNestedYamlIO(TestCase):
    def setUp(self):
        self.input_file = Path(__file__).parent / ".." / "examples" / "schema1.yaml"

    def test_import_nested_yaml_dry_run(self):
        # Test a dry run
        call_command("import", "--dry-run", self.input_file)
        check_db_size(
            self,
            entity_len=0,
            format_spec_len=0,
            quantity_len=0,
            data_file_len=0,
            release_len=0,
        )

    def test_import_nested_yaml(self):
        # Test a normal import
        call_command("import", self.input_file)
        check_db_size(
            self,
            entity_len=12,
            format_spec_len=3,
            quantity_len=12,
            data_file_len=3,
            release_len=1,
        )
        check_deps_in_schema(self)

    def test_import_nested_yaml_no_overwrite(self):
        # Test that --no-overwrite works
        call_command("import", "--no-overwrite", self.input_file)
        check_db_size(
            self,
            entity_len=12,
            format_spec_len=3,
            quantity_len=12,
            data_file_len=3,
            release_len=1,
        )
        check_deps_in_schema(self)


class TestPlainYamlIO(TestCase):
    def test_import_plain_yaml(self):
        input_file = Path(__file__).parent / ".." / "examples" / "schema2.yaml"
        call_command("import", input_file)
        check_db_size(
            self,
            entity_len=12,
            format_spec_len=3,
            quantity_len=12,
            data_file_len=3,
            release_len=1,
        )
        check_deps_in_schema(self)


class TestTutorial(TestCase):
    def test_import_tutorial(self):
        input_file = Path(__file__).parent / ".." / "examples" / "tutorial.yaml"
        call_command("import", input_file)
        check_db_size(
            self,
            entity_len=6,
            format_spec_len=6,
            quantity_len=9,
            data_file_len=0,
            release_len=0,
        )
