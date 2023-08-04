# -*- encoding: utf-8 -*-

from django.core.management.base import BaseCommand
from browse.models import DataFile, Release


class Command(BaseCommand):
    help = "Delete data files from the database"
    output_transaction = True
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--release",
            action="append",
            type=str,
            help="Delete all the objects in the matching release. "
            "This switch can be repeated.",
        )
        parser.add_argument(
            "--from-file",
            type=str,
            help="Read the UUIDs of the objects to be deleted from file (one UUID per line)",
        )
        parser.add_argument(
            "uuids",
            nargs="*",
            type=str,
            help="""List of the UUIDs of the data files to be removed""",
        )

    def handle(self, *args, **options):
        from uuid import UUID
        import time

        ######################################################
        # Let's build the list of UUIDs to delete.

        # First comes the plain list of UUIDs provided through the command line
        list_of_uuids = [UUID(x) for x in options["uuids"]]

        # Then the UUIDs provided through a file
        if options.get("from_file", None) is not None:
            with open(options["from_file"], "rt") as input_file:
                list_of_uuids += [UUID(x.strip()) for x in input_file.readlines()]

        # Next the list of releases
        releases = options.get("release", [])
        num_of_objects_in_releases = {}
        if releases:
            for cur_release in releases:
                cur_num = 0
                for cur_obj in DataFile.objects.filter(release_tags=cur_release):
                    # Only delete this object if it does not belong to any
                    # other release, otherwise there would be dangling references
                    if len(cur_obj.release_tags.all()) == 1:
                        list_of_uuids.append(cur_obj.pk)
                        cur_num += 1

                if cur_num > 0:
                    num_of_objects_in_releases[cur_release] = cur_num

        ########################################################
        # Delete the objects

        queryset = DataFile.objects.filter(pk__in=list_of_uuids)

        num_of_objects = len(queryset)
        if num_of_objects == 0:
            print(
                f"No objects matching the {len(list_of_uuids)} UUID(s) have been found"
            )
            return

        print(f"Found {num_of_objects} data file(s) out of {len(list_of_uuids)}")

        start_time = time.monotonic()
        queryset.delete()
        end_time = time.monotonic()
        print(
            f"The {num_of_objects} object(s) have been deleted in {end_time - start_time:.2f} s"
        )

        for cur_release, cur_num_of_objs in num_of_objects_in_releases.items():
            Release.objects.filter(tag=cur_release).delete()
            print(
                f"Release {cur_release} deleted, it contained {cur_num_of_objs} data files"
            )
