# -*- encoding: utf-8 -*-

from pathlib import Path
import json
from uuid import UUID
import yaml

from django.core.files import File
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from django.core.management.base import BaseCommand, CommandError
from browse.models import (
    Entity,
    Quantity,
    DataFile,
    FormatSpecification,
    Release,
    update_release_file_dumps,
)


def spaces(nest_level):
    return " " * (nest_level * 2)


def build_query_from_uuid_or_name(key, name_field="name"):
    """Return the list of arguments to a 'get' method for a Django's model

    If "key" is a valid UUID, the function returns the dictionary associating
    "uuid" (string) with the key, otherwise it associates "name" with the key.

    This can be used in the following code::

      Model.object.get(**build_query_from_uuid_or_name(key))
    """

    try:
        _ = UUID(key, version=4)
        query = {"uuid": key}
    except ValueError:
        query = {name_field: key}

    return query


class Command(BaseCommand):
    help = "Load records into the database from a JSON file"
    output_transaction = True
    requires_migrations_checks = True

    def create_entities(self, entities, parent=None, nest_level=0):
        for entity_dict in entities:
            cur_entity_name = entity_dict.get("name")
            uuid = entity_dict.get("uuid")

            if uuid:
                self.stdout.write(
                    spaces(nest_level) + f"Entity {cur_entity_name} ({uuid[0:6]})"
                )
            else:
                self.stdout.write(spaces(nest_level) + f"Entity {cur_entity_name}")

            if not self.dry_run:
                cur_entity = Entity.objects.filter(uuid=uuid)
                if not (self.no_overwrite and cur_entity):
                    (cur_entity, _) = Entity.objects.update_or_create(
                        uuid=uuid,
                        defaults={
                            "name": cur_entity_name,
                            "parent": parent,
                        },
                    )
                else:
                    cur_entity = cur_entity[0]
            else:
                cur_entity = cur_entity_name

            if "quantities" in entity_dict:
                self.create_quantities(
                    entity_dict["quantities"],
                    parent_entity=cur_entity,
                    nest_level=nest_level + 1,
                )

            if not self.dry_run:
                cur_entity.save()

            # Recursively create children
            self.create_entities(
                entity_dict.get("children", []),
                parent=cur_entity,
                nest_level=nest_level + 1,
            )

    def create_format_specifications(self, specs):
        for spec_dict in specs:
            document_ref = spec_dict.get("document_ref")
            uuid = spec_dict.get("uuid")
            if self.no_overwrite and FormatSpecification.objects.filter(uuid=uuid):
                self.stdout.write(
                    f"Format specification {document_ref} already exists in the database"
                )
                continue

            uuid = spec_dict.get("uuid")
            doc_file_name = spec_dict.get("doc_file")

            if doc_file_name:
                file_path = self.attachment_source_path / doc_file_name
                try:
                    fp = open(file_path, "rb")
                except FileNotFoundError:
                    file_path = (
                        self.attachment_source_path / "format_spec" / doc_file_name
                    )
                    fp = open(file_path, "rb")

                doc_file = File(fp, "rb")
            else:
                file_path = "<no file>"
                fp = None
                doc_file = None

            if uuid:
                self.stdout.write(
                    f'Format specification "{document_ref}" ({uuid[0:6]}, {file_path})'
                )
            else:
                self.stdout.write(
                    f'Format specification "{document_ref}" ({file_path})'
                )

            title = spec_dict.get("title", "")
            doc_mime_type = spec_dict.get("doc_mime_type", "")
            file_mime_type = spec_dict.get("file_mime_type", "")

            if not self.dry_run:
                (format_spec, _) = FormatSpecification.objects.update_or_create(
                    uuid=uuid,
                    defaults={
                        "document_ref": document_ref,
                        "title": title,
                        "doc_file": doc_file,
                        "doc_file_name": doc_file_name,
                        "doc_mime_type": doc_mime_type,
                        "file_mime_type": file_mime_type,
                    },
                )

                format_spec.save()

            if fp:
                fp.close()

    def create_quantities(self, quantities, parent_entity=None, nest_level=0):
        for quantity_dict in quantities:
            name = quantity_dict.get("name")
            uuid = quantity_dict.get("uuid")
            if uuid:
                if self.no_overwrite and Quantity.objects.filter(uuid=uuid):
                    self.stdout.write(
                        spaces(nest_level)
                        + f"Quantity {name} already exists in the database"
                    )
                    continue

                self.stdout.write(spaces(nest_level) + f"Quantity {name} ({uuid[0:6]})")
            else:
                self.stdout.write(spaces(nest_level) + f"Quantity {name}")

            entity = parent_entity
            if not entity:
                parent_uuid = quantity_dict.get("entity")
                if not parent_uuid:
                    raise CommandError(f"expected entity for quantity {name}")

                try:
                    entity = Entity.objects.get(uuid=parent_uuid)

                except Entity.DoesNotExist:
                    raise CommandError(
                        f"parent {parent_uuid[0:6]} for {name} "
                        f"({uuid[0:6]}) does not exist"
                    )

            format_spec_ref = quantity_dict.get("format_spec")
            format_spec = None
            if format_spec_ref:
                try:
                    format_spec = FormatSpecification.objects.get(
                        **build_query_from_uuid_or_name(
                            format_spec_ref, name_field="document_ref"
                        )
                    )
                except FormatSpecification.DoesNotExist:
                    self.stderr.write(
                        f"Error, format specification {format_spec_ref} "
                        f"for quantity {name} ({uuid[0:6]}) does not exist"
                    )

            if self.dry_run:
                continue

            (quantity, _) = Quantity.objects.update_or_create(
                uuid=uuid,
                defaults={
                    "name": name,
                    "format_spec": format_spec,
                    "parent_entity": entity,
                },
            )

            if "data_files" in quantity_dict:
                self.create_data_files(
                    quantity_dict["data_files"],
                    parent_quantity=quantity,
                    nest_level=nest_level + 1,
                )

            quantity.save()

    def create_data_files(self, data_files, parent_quantity=None, nest_level=0):
        for data_file_dict in data_files:
            name = data_file_dict.get("name")
            uuid = data_file_dict.get("uuid")
            if self.no_overwrite and DataFile.objects.filter(uuid=uuid):
                self.stdout.write(
                    spaces(nest_level)
                    + f"Data file {name} already exists in the database"
                )
                continue

            metadata = json.dumps(data_file_dict.get("metadata", {}))
            filename = data_file_dict.get("file_data")
            plot_filename = data_file_dict.get("plot_file")
            dependencies = data_file_dict.get("dependencies", [])

            try:
                upload_date = parse_datetime(data_file_dict.get("upload_date"))

                if not is_aware(upload_date):
                    upload_date = make_aware(upload_date)
            except ValueError as exc:
                raise CommandError(
                    f"invalid upload date for data file {name} ({uuid[0:6]}): {exc}"
                )

            if not upload_date:
                raise CommandError(
                    f"no upload date specified for data file {name} ({uuid[0:6]})"
                )

            if filename:
                file_path = self.attachment_source_path / filename
                try:
                    fp = open(file_path, "rb")
                except FileNotFoundError:
                    file_path = self.attachment_source_path / "data_files" / filename
                    fp = open(file_path, "rb")
                file_data = File(fp, "rb")
            else:
                fp = None
                file_data = None

            if plot_filename:
                file_path = self.attachment_source_path / plot_filename
                try:
                    plot_fp = open(file_path, "rb")
                except FileNotFoundError:
                    file_path = (
                        self.attachment_source_path / "plot_files" / plot_file_name
                    )
                    plot_fp = open(file_path, "rb")
                plot_file = File(plot_fp, "rb")
            else:
                plot_fp = None
                plot_file = None

            if uuid:
                self.stdout.write(
                    spaces(nest_level) + f'Data file "{name}" ({uuid[0:6]}, {filename})'
                )
            else:
                self.stdout.write(
                    spaces(nest_level) + f'Data file "{name}" ({filename})'
                )

            for cur_dep in dependencies:
                self.stdout.write(spaces(nest_level) + f"  Depends on {cur_dep[0:6]}")

            if self.dry_run:
                continue

            quantity = parent_quantity
            if not quantity:
                parent_uuid = data_file_dict.get("quantity", "")
                quantity = Quantity.objects.get(uuid=parent_uuid)

            (cur_data_file, _) = DataFile.objects.update_or_create(
                uuid=uuid,
                defaults={
                    "name": name,
                    "upload_date": upload_date,
                    "metadata": metadata,
                    "file_data": file_data,
                    "quantity": quantity,
                    "spec_version": data_file_dict.get("spec_version"),
                    "plot_file": plot_file,
                    "plot_mime_type": data_file_dict.get("plot_mime_type"),
                },
            )

            for cur_dep in dependencies:
                reference = DataFile.objects.get(uuid=cur_dep)
                cur_data_file.dependencies.add(reference)

            cur_data_file.save()

            if fp:
                fp.close()
            if plot_fp:
                plot_fp.close()

    def create_releases(self, releases):
        for rel_dict in releases:
            tag = rel_dict.get("tag")
            if self.no_overwrite and Release.objects.filter(tag=tag):
                self.stdout.write(f"Release {tag} already exists in the database")
                continue

            comment = rel_dict.get("comment")
            data_files = rel_dict.get("data_files")

            try:
                rel_date = parse_datetime(rel_dict.get("release_date"))
            except ValueError as err:
                raise CommandError(f"invalid date for release {tag}: {err}")

            if not rel_date.tzinfo:
                rel_date = make_aware(rel_date)

            if not rel_date:
                raise CommandError(f"no date specified for release {tag}")

            self.stdout.write(
                f'Release tag "{tag}" ({rel_date}), {len(data_files)} objects'
            )

            if not self.dry_run:
                (cur_release, _) = Release.objects.update_or_create(
                    tag=tag,
                    defaults={"rel_date": rel_date, "comment": comment},
                )

                for cur_uuid in data_files:
                    cur_release.data_files.add(DataFile.objects.get(uuid=cur_uuid))

                cur_release.save()

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not execute any action on the database (useful for testing)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Unused",
        )
        parser.add_argument(
            "--no-overwrite",
            action="store_true",
            help="Do not overwrite existing objects in the database.",
        )
        parser.add_argument(
            "schema_file",
            nargs="+",
            help="""
YAML/JSON file containing the specification of the records to be imported
int the database. All the attachments (data files, specification documents,
etc.) will be looked in the directory where this file resides.
""",
            type=str,
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.use_json = options["json"]
        self.no_overwrite = options["no_overwrite"]

        for curfile in options["schema_file"]:
            schema_filename = Path(curfile)

            # Retrieve every attachment from the same path where the
            # JSON file is
            self.attachment_source_path = schema_filename.parent

            with schema_filename.open("rt") as inpf:
                if schema_filename.suffix == ".yaml":
                    schema = yaml.safe_load(inpf)
                else:
                    schema = json.load(inpf)

            self.create_format_specifications(schema.get("format_specifications", []))
            self.create_entities(schema.get("entities", []))
            self.create_quantities(schema.get("quantities", []))
            self.create_data_files(schema.get("data_files", []))
            self.create_releases(schema.get("releases", []))

        update_release_file_dumps()
