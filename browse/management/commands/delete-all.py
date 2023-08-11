# -*- encoding: utf-8 -*-

import sys

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from browse.models import DataFile, Quantity, Entity, Release, FormatSpecification


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    See StackOverflow: https://tinyurl.com/4jb3a4pe
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n')")


class Command(BaseCommand):
    help = "Delete all objects of the same kind from the database"
    output_transaction = True
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Do not ask for confirmation before deleting stuff (USE WITH CARE)",
        )
        parser.add_argument(
            "--delete-authentication",
            action="store_true",
            default=False,
            help="Delete all the authentication data too",
        )

        parser.add_argument(
            "--skip-format-specifications",
            action="store_true",
            default=False,
            help="Do not delete the format specifications",
        )

        parser.add_argument(
            "--only-data-files",
            action="store_true",
            default=False,
            help="""Only delete all the data files, but leave
            entities, quantities, and format specifications intact""",
        )

    def handle(self, *args, **options):
        if options["delete_authentication"]:
            question = (
                "This will delete *everything* from the database. " "Are you sure?"
            )
            delete_auth = True
        else:
            question = (
                "This will delete all format specifications and the "
                "entity/quantity tree. Are you sure?"
            )
            delete_auth = False

        if (not options["force"]) and (
            not query_yes_no(question=question, default="no")
        ):
            return

        import time

        start_time = time.monotonic()

        DataFile.objects.filter().delete()

        if not options["only_data_files"]:
            Quantity.objects.filter().delete()
            Entity.objects.filter().delete()
            Release.objects.filter().delete()

            if not options["skip_format_specifications"]:
                FormatSpecification.objects.filter().delete()

        if delete_auth:
            User.objects.filter().delete()
            Group.objects.filter().delete()

        end_time = time.monotonic()
        print(f"Task completed in {end_time - start_time:0.2f} s")
