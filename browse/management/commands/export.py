# -*- encoding: utf-8 -*-

from pathlib import Path

from django.core.management.base import BaseCommand

from browse.models import (
    ReleaseDumpConfiguration,
    DumpOutputFormat,
    dump_db_to_json,
)


class Command(BaseCommand):
    help = "Exports the contents of a database into a local directory"
    output_transaction = False
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-attachments",
            action="store_true",
            help="Do not save data files, only the JSON file",
        )
        parser.add_argument(
            "--only-tree",
            action="store_true",
            help="Only include entities and quantities in the JSON file",
        )
        parser.add_argument(
            "--json",
            default=True,
            action="store_true",
            help="Use JSON as the format of the file containing the schema "
            "(always true)",
        )
        parser.add_argument(
            "--yaml",
            action="store_true",
            help="Save a copy of the schema using the YAML format (useful "
            "for legacy codes)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite anything that is already present in the output path",
        )
        parser.add_argument(
            "--release",
            type=str,
            default=None,
            help="""
Name of the release to include in the output, e.g., 'v1.3'. If
it is not present, all releases will be included in the output.
""",
        )
        parser.add_argument(
            "--skip-empty-entities",
            action="store_true",
            help="""
If set, skip all those entities that have no sub-entities nor
quantities. See also --skip-empty-quantities.
""",
        )
        parser.add_argument(
            "--skip-empty-quantities",
            action="store_true",
            help="""
If set, skip all those quantities that have no data files.
(This can be useful if you are using --release=REL to
export just one release, as some quantities might have been
included because of a different release.)
""",
        )
        parser.add_argument(
            "output_path",
            help="""
Directory where to store the contents of the database.
If the folder does not exist, it will be created.""",
            type=str,
        )

    def handle(self, *args, **options):
        dump_db_to_json(
            ReleaseDumpConfiguration(
                no_attachments=options["no_attachments"],
                exist_ok=options["force"],
                output_format=(
                    DumpOutputFormat.JSON if options["json"] else DumpOutputFormat.YAML
                ),
                skip_empty_quantities=options["skip_empty_quantities"],
                skip_empty_entities=options["skip_empty_entities"],
                only_tree=options["only_tree"],
                output_folder=Path(options["output_path"]),
            ),
            release_tag=options["release"],
        )
