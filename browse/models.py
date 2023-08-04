# -*- encoding: utf-8 -*-

"""Implementation of the fundamental concepts of an IMO as database
tables.

This file implements the following classes, which are descendeants of
Django's `models.Model` class and are therefore used to set up tables
in the database:

- `Entity`: a feature of the instrument that is modelled in the
  IMO. Entities can form tree-like structures. Examples: a telescope,
  a cryostat, a focal plane, a beam, etc., where focal planes can be
  parents of several beams.

- `Quantity`: numerical information related to an entity, which must
  conform to some format specification (see below). Examples: a beam
  pattern saved as a Healpix map, a bandpass stored in an Excel file,
  etc.

- `FormatSpecification`: a document that presents the mathematical
  model, the units of measure used, the assumptions, and the file
  format used for files storing a "quantity" (see above)

- `DataFile`: a file containing numerical estimates of some
  "quantity" (see above).

"""

from collections import namedtuple, OrderedDict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

import uuid
from typing import Optional

import git
import json
import yaml
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from instrumentdb import __version__

FileType = namedtuple(
    "ImageFileType",
    [
        "mime_type",
        "file_extension",
        "description",
    ],
)

# List of supported document types (for specification documents).
# Please keep the most useful at the top of the list, then use
# alphabetic order!
DOCUMENT_FILE_TYPES = [
    FileType(mime_type="text/plain", file_extension="txt", description="Plain text"),
    FileType(mime_type="text/html", file_extension="html", description="HTML"),
    FileType(
        mime_type="application/pdf", file_extension="pdf", description="Adobe PDF"
    ),
    FileType(
        mime_type="text/rtf",
        file_extension="rtf",
        description="Rich-Text Format (.rtf)",
    ),
    FileType(mime_type="text/markdown", file_extension="md", description="Markdown"),
    FileType(
        mime_type="application/x-abiword",
        file_extension="abw",
        description="AbiWord document",
    ),
    FileType(
        mime_type="application/msword",
        file_extension="doc",
        description="Microsoft Word (.doc)",
    ),
    FileType(
        mime_type="application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
        file_extension="docx",
        description="Microsoft Word (.docx)",
    ),
    FileType(
        mime_type="application/vnd.amazon.ebook",
        file_extension="azw",
        description="Amazon Kindle eBook",
    ),
    FileType(
        mime_type="application/epub+zip",
        file_extension="epub",
        description="Electronic publication (EPUB)",
    ),
    FileType(
        mime_type="application/vnd.oasis.opendocument.text",
        file_extension="",
        description="OpenDocument text document (.odt)",
    ),
    FileType(
        mime_type="application/vnd.oasis.opendocument.presentation",
        file_extension="odp",
        description="OpenDocument presentation document (.odp)",
    ),
    FileType(
        mime_type="application/vnd.oasis.opendocument.spreadsheet",
        file_extension="ods",
        description="OpenDocument spreadsheet document (.ods)",
    ),
    FileType(
        mime_type="application/vnd.ms-powerpoint",
        file_extension="ppt",
        description="Microsoft PowerPoint (.ppt)",
    ),
    FileType(
        mime_type="application/vnd.openxmlformats-officedocument"
        ".presentationml.presentation",
        file_extension="docx",
        description="Microsoft PowerPoint (.pptx)",
    ),
    FileType(
        mime_type="application/vnd.ms-excel",
        file_extension="xls",
        description="Microsoft Excel (.xls)",
    ),
    FileType(
        mime_type="application/vnd.openxmlformats-officedocument"
        ".spreadsheetml.sheet",
        file_extension="xlsx",
        description="Microsoft Excel (.xlsx)",
    ),
    FileType(
        mime_type="application/octet-stream",
        file_extension="bin",
        description="Other (unknown)",
    ),
]

# List of supported image types (for plots associated with data files)
IMAGE_FILE_TYPES = [
    FileType(mime_type="image/png", file_extension="png", description="PNG image"),
    FileType(mime_type="image/jpeg", file_extension="jpg", description="Jpeg image"),
    FileType(mime_type="image/svg+xml", file_extension="svg", description="SVG image"),
    FileType(mime_type="image/apng", file_extension="apng", description="Animated PNG"),
    FileType(
        mime_type="image/bmp", file_extension="bmp", description="Windows bitmap image"
    ),
    FileType(mime_type="image/gif", file_extension="gif", description="GIF image"),
    FileType(mime_type="image/x-icon", file_extension="ico", description="ICO image"),
    FileType(mime_type="image/tiff", file_extension="tif", description="TIFF image"),
    FileType(mime_type="image/webp", file_extension="webp", description="WebP image"),
    FileType(
        mime_type="application/octet-stream",
        file_extension="bin",
        description="Other (unknown)",
    ),
]

# These dictionaries associate a MIME type with its extension:
# MIME_TO_IMAGE_EXTENSION["image/tiff"] == "tif"
MIME_TO_DOC_EXTENSION = {x.mime_type: x.file_extension for x in DOCUMENT_FILE_TYPES}
MIME_TO_IMAGE_EXTENSION = {x.mime_type: x.file_extension for x in IMAGE_FILE_TYPES}


def validate_json(value):
    """Check that `value` is a valid JSON record"""

    try:
        json.loads(value)
    except json.JSONDecodeError as err:
        raise ValidationError(
            'Invalid JSON: "%(value)s", reason: %(err)s',
            params={"value": value, "err": str(err)},
        )


class Entity(MPTTModel):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(
        max_length=256, help_text="Descriptive name for this entity"
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "entities"


def format_spec_directory_path(instance, filename):
    """This is called by the FileField of a format spec

    It returns the path where to save a format specification
    """

    # The ".split" trick enables proper treatment of MIME types like
    # "text/markdown; charset=UTF-8", because it removes what comes
    # after the ";"
    ext = MIME_TO_DOC_EXTENSION[instance.doc_mime_type.split(";")[0]]

    true_file_name = instance.doc_file_name
    if not true_file_name:
        true_file_name = ext

    return Path("format_spec") / f"{instance.uuid}_{true_file_name}"


class FormatSpecification(models.Model):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    document_ref = models.CharField(
        "ID of the specification document",
        max_length=64,
        unique=True,
        help_text="ID of the technical document",
    )
    title = models.CharField(
        max_length=256,
        help_text="Title of the document containing the specification "
        + "for a file format",
    )
    doc_file = models.FileField(
        "file containing the specification document",
        null=True,
        blank=True,
        upload_to=format_spec_directory_path,
        help_text="Downloadable copy of the specification document (optional)",
    )
    doc_file_name = models.CharField(
        "name of the file containing the specification document",
        max_length=256,
        null=True,
        blank=True,
        help_text="Name of the file containing the specification document (optional)",
    )
    # Regarding the maximum length of a MIME type, see
    # https://stackoverflow.com/questions/643690/maximum-mimetype-length-when-storing-type-in-db
    doc_mime_type = models.CharField(
        "MIME type of the specification document",
        max_length=256,
        choices=[(x.mime_type, x.description) for x in DOCUMENT_FILE_TYPES],
        default=DOCUMENT_FILE_TYPES[0].mime_type,
        help_text="This specifies the MIME type of the downloadable copy "
        + "of the specification document",
    )
    file_mime_type = models.CharField(
        "MIME type of the file",
        max_length=256,
        help_text="This specifies the MIME type of the data file",
    )

    def __str__(self):
        if self.title:
            return f'{self.document_ref} ("{self.title}")'
        else:
            return f"{self.document_ref}"


class Quantity(models.Model):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(
        max_length=256, help_text="Descriptive name for this quantity"
    )
    format_spec = models.ForeignKey(
        FormatSpecification,
        on_delete=models.CASCADE,
        related_name="quantities",
        help_text="Reference to the format specification used for data files "
        + "associated with this quantity",
    )
    parent_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="quantities",
        help_text="Entity to whom this quantity is related",
    )

    def __str__(self):
        return f"{self.name} ({self.uuid.hex[0:8]})"

    class Meta:
        verbose_name_plural = "quantities"
        ordering = (
            "name",
            "uuid",
        )


def data_file_directory_path(instance, filename):
    return Path("data_files") / f"{instance.uuid}_{instance.name}"


def plot_file_directory_path(instance, filename):
    ext = MIME_TO_IMAGE_EXTENSION[instance.plot_mime_type.split(";")[0]]
    return Path("plot_files") / f"{instance.uuid}_{instance.name}.{ext}"


class DataFile(models.Model):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(
        "file name", max_length=1024, default="noname", help_text="Name of the file"
    )
    upload_date = models.DateTimeField(
        "date when the file was uploaded",
        default=timezone.now,
        help_text="Date when the file was added to the database",
    )
    metadata = models.TextField(
        "JSON-formatted metadata",
        max_length=32768,
        blank=True,
        help_text="JSON record containing metadata for the file",
        validators=[validate_json],
    )
    file_data = models.FileField(
        "file",
        blank=True,
        upload_to=data_file_directory_path,
        help_text="File contents (when present)",
    )
    quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="data_files",
        help_text="Quantity associated with the data in this file",
    )
    spec_version = models.CharField(
        "version of the specification document",
        max_length=32,
        help_text="Version number of the format specification document",
    )
    dependencies = models.ManyToManyField(
        "DataFile",
        blank=True,
        help_text="List of data files that have been used as inputs to "
        + "produce this data file",
    )
    plot_file = models.FileField(
        "image file",
        blank=True,
        upload_to=plot_file_directory_path,
        help_text="Plot of the data in the file (optional)",
    )
    plot_mime_type = models.CharField(
        "MIME type of the image",
        max_length=256,
        blank=True,
        null=True,
        choices=[(x.mime_type, x.description) for x in IMAGE_FILE_TYPES],
        default=None,
        help_text="This specifies the MIME type of the image",
    )

    # This points to a release. It is used only for data files that
    # belong to official releases of an Instrument Database. We use a
    # many-to-many relationship, as a data file might be part of
    # several data releases (if it was never updated as time passed).
    release_tags = models.ManyToManyField(
        "Release", blank=True, related_name="data_files"
    )

    comment = models.TextField(max_length=4096, blank=True, help_text="Free-form notes")

    def __str__(self):
        return f"{self.name} ({self.uuid.hex[0:8]})"

    class Meta:
        # When querying *all* the DataFile objects in a database, the
        # (inverse) order by upload date will not be very meaningful… But
        # usually we query only for DataFile objects related to some
        # specific quantity, and in this case the ordering is what we
        # would expect: the first object is the most recent one!
        ordering = (
            "-upload_date",
            "name",
            "uuid",
        )

    @property
    def full_path(self):
        entity = self.quantity.parent_entity
        ancestors = entity.get_ancestors(include_self=True)
        return "/".join([x.name for x in ancestors]) + "/" + self.name


class Release(models.Model):
    tag = models.CharField(
        "version tag",
        max_length=32,
        primary_key=True,
        unique=True,
        help_text="String uniquely identifying the version",
    )

    rel_date = models.DateTimeField(
        "release date",
        default=timezone.now,
        editable=True,
        help_text="Release date of the tag",
    )

    comment = models.CharField(max_length=4096, blank=True, help_text="Free-form text")

    json_file = models.FileField(
        blank=True,
        editable=False,
        upload_to="",
        help_text="A JSON dump of the release, ready to be downloaded",
    )

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        if bool(self.json_file):
            # The JSON dump already exists
            return

        with TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            json_file_path = dump_db_to_json(
                ReleaseDumpConfiguration(
                    no_attachments=True,
                    only_tree=False,
                    exist_ok=True,
                    output_format=DumpOutputFormat.JSON,
                    output_folder=temp_path,
                ),
                release_tag=str(self.tag),
            )

            with json_file_path.open("rt") as json_file:
                self.json_file.save(
                    name=f"schema_{self.tag}.json",
                    content=File(json_file),
                )

        return result


############################################################################


class DumpOutputFormat(Enum):
    JSON = 1
    YAML = 2


@dataclass
class ReleaseDumpConfiguration:
    no_attachments: bool
    only_tree: bool
    exist_ok: bool
    output_format: DumpOutputFormat
    output_folder: Path


# File dump is done in chunks; this variable specifies the
# size of one chunk (in bytes)
COPY_CHUNK_SIZE = 1024 * 1024

# This is used as a wrapper to strings that must be quoted in YAML
# output. Consider the following code:
#
#     yaml.dumps({"a": "hello"})
#
# This produces:
#
#     a: hello
#
# Instead, the following code
#
#     yaml.dumps({"a": Quoted("hello")})
#
# produces
#
#     a: "hello"
#
# I find the latter more readable, and it prevents some of the
# problems outlined in this article:
#
#     https://www.arp242.net/yaml-config.html


class Quoted(str):
    pass


# Taken from
# https://stackoverflow.com/questions/5121931/
# /in-python-how-can-you-load-yaml-mappings-as-ordereddicts
def yaml_saner_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _quoted_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()
        )

    OrderedDumper.add_representer(Quoted, _quoted_representer)

    # This enables the serialization of OrderedDict objects
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def save_attachment(configuration: ReleaseDumpConfiguration, relative_path, file_data):
    """Save a file into the specified path under the output folder

    This function is used to save specification documents, data
    files and plot files.

    The parameter "relative_path" specifies the sub-folder *and*
    file name, which is considered relative to self.output_folder
    (set within Command.handle).

    """
    abs_path = configuration.output_folder / relative_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)

    with file_data.open("rb") as inpf, abs_path.open("wb") as outf:
        while True:
            data = inpf.read(COPY_CHUNK_SIZE)
            if not data:  # end of file reached
                break
            outf.write(data)


def dump_entity_tree(configuration: ReleaseDumpConfiguration, entities):
    result = []
    for cur_entity in entities:
        # We use a OrderedDict here because otherwise "children" would
        # be the first key in the JSON file, and this would make the
        # file harder to read
        new_element = OrderedDict(
            [("uuid", Quoted(cur_entity.uuid)), ("name", Quoted(cur_entity.name))]
        )

        # Add the "children" key at the bottom of the list of keys
        children = cur_entity.get_children()
        if children:
            # Descend the tree recursively
            new_element["children"] = dump_entity_tree(configuration, children)

        result.append(new_element)

    return result


def dump_specifications(configuration: ReleaseDumpConfiguration, specs):
    result = []
    for cur_spec in specs:
        cur_entry = OrderedDict(
            [
                ("uuid", Quoted(cur_spec.uuid)),
                ("document_ref", Quoted(cur_spec.document_ref)),
                ("title", Quoted(cur_spec.title)),
                ("file_mime_type", Quoted(cur_spec.file_mime_type)),
                ("doc_mime_type", Quoted(cur_spec.doc_mime_type)),
            ]
        )

        if cur_spec.doc_file_name and (not configuration.no_attachments):
            dest_path = (
                Path("format_spec") / f"{cur_spec.uuid}_{cur_spec.doc_file_name}"
            )
            cur_entry["file_name"] = Quoted(dest_path)

            save_attachment(configuration, dest_path, cur_spec.doc_file)

        result.append(cur_entry)

    return result


def dump_quantities(configuration: ReleaseDumpConfiguration, quantities):
    result = []
    for cur_quantity in quantities:
        cur_entry = OrderedDict(
            [
                ("uuid", Quoted(cur_quantity.uuid)),
                ("name", Quoted(cur_quantity.name)),
                ("format_spec", Quoted(cur_quantity.format_spec.uuid)),
                ("entity", Quoted(cur_quantity.parent_entity.uuid)),
            ]
        )

        result.append(cur_entry)

    return result


def dump_data_files(configuration: ReleaseDumpConfiguration, data_files):
    result = []
    for cur_data_file in data_files:
        cur_entry = OrderedDict(
            [
                ("uuid", Quoted(cur_data_file.uuid)),
                ("name", Quoted(cur_data_file.name)),
                ("upload_date", Quoted(cur_data_file.upload_date)),
                ("metadata", json.loads(cur_data_file.metadata)),
                ("quantity", Quoted(cur_data_file.quantity.uuid)),
                ("spec_version", Quoted(cur_data_file.spec_version)),
            ]
        )

        if cur_data_file.file_data and (not configuration.no_attachments):
            dest_path = (
                Path("data_files") / f"{cur_data_file.uuid}_{cur_data_file.name}"
            )
            cur_entry["file_name"] = Quoted(dest_path)

            save_attachment(configuration, dest_path, cur_data_file.file_data)

        if cur_data_file.plot_file and (not configuration.no_attachments):
            dest_path = (
                Path("plot_files") / plot_file_directory_path(cur_data_file, "").name
            )
            cur_entry["plot_file"] = Quoted(dest_path)
            cur_entry["plot_mime_type"] = Quoted(cur_data_file.plot_mime_type)
            save_attachment(configuration, dest_path, cur_data_file.file_data)

        if cur_data_file.dependencies:
            cur_entry["dependencies"] = [
                Quoted(x.uuid) for x in cur_data_file.dependencies.all()
            ]

        result.append(cur_entry)

    return result


def dump_releases(configuration: ReleaseDumpConfiguration, releases):
    result = []
    for cur_release in releases:
        cur_entry = OrderedDict(
            [
                ("tag", Quoted(cur_release.tag)),
                ("release_date", Quoted(cur_release.rel_date)),
                ("comment", Quoted(cur_release.comment)),
                (
                    "data_files",
                    [Quoted(x.uuid) for x in cur_release.data_files.all()],
                ),
            ]
        )

        result.append(cur_entry)

    return result


def save_schema(
    configuration: ReleaseDumpConfiguration,
    output_file_path,
    release_tag: Optional[str] = None,
):
    try:
        this_repo = git.Repo(search_parent_directories=True)
        git_sha = this_repo.head.object.hexsha
    except git.InvalidGitRepositoryError:
        git_sha = "unknown"

    if release_tag:
        release_tag = [Release.objects.get(tag=release_tag)]
        data_files = release_tag[0].data_files.all()
    else:
        # If no release is specified, return *everything*
        release_tag = Release.objects.all()
        data_files = DataFile.objects.all()

    schema = OrderedDict(
        [
            (
                "instrumentdb",
                OrderedDict(
                    [
                        ("git_sha", git_sha),
                        ("version", Quoted(__version__)),
                        ("dump_date", timezone.now().isoformat()),
                        (
                            "repository",
                            Quoted("https://github.com/ziotom78/instrumentdb"),
                        ),
                    ]
                ),
            ),
            ("entities", dump_entity_tree(configuration, Entity.objects.root_nodes())),
            (
                "format_specifications",
                {}
                if configuration.only_tree
                else dump_specifications(
                    configuration, FormatSpecification.objects.all()
                ),
            ),
            ("quantities", dump_quantities(configuration, Quantity.objects.all())),
            (
                "data_files",
                {}
                if configuration.only_tree
                else dump_data_files(configuration, data_files),
            ),
            (
                "releases",
                {}
                if configuration.only_tree
                else dump_releases(configuration, release_tag),
            ),
        ]
    )

    dump_functions = {
        DumpOutputFormat.JSON: lambda output_stream: json.dump(
            schema, output_stream, indent=2
        ),
        DumpOutputFormat.YAML: lambda output_stream: yaml_saner_dump(
            schema, stream=output_stream
        ),
    }

    with output_file_path.open("w") as output_file:
        dump_fn = dump_functions[configuration.output_format]
        dump_fn(output_stream=output_file)


def dump_db_to_json(
    configuration: ReleaseDumpConfiguration, release_tag: Optional[str] = None
) -> Path:
    """Save the database into a JSON/YAML file

    This function creates a output folder and dumps the whole database in it. If
    `release_tag` is set to some string, only the release matching that string
    (e.g., ``v1.3``) will be considered when saving data files. Quantities, entities,
    and format specifications are always saved in full.

    The function returns a ``Path`` object to the schema file that has been created.
    """

    configuration.output_folder.mkdir(parents=True, exist_ok=configuration.exist_ok)

    extensions = {
        DumpOutputFormat.JSON: "json",
        DumpOutputFormat.YAML: "yaml",
    }
    cur_ext = extensions[configuration.output_format]

    output_schema_path = configuration.output_folder / f"schema.{cur_ext}"
    save_schema(
        configuration,
        output_schema_path,
        release_tag=release_tag,
    )

    return output_schema_path


def update_release_file_dumps(force: bool = False):
    """
    Update the field `json_file` for each `Release` object.
    """

    for cur_release in Release.objects.all():
        if bool(cur_release.json_file) and (not force):
            # The JSON dump already exists, and we are not required
            # to recreate it, so let's skip this release
            continue

        with TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            json_file_path = dump_db_to_json(
                ReleaseDumpConfiguration(
                    no_attachments=True,
                    exist_ok=True,
                    output_format=DumpOutputFormat.JSON,
                    output_folder=temp_path,
                ),
                release_tag=cur_release.tag,
            )

            with json_file_path.open("rt") as json_file:
                cur_release.json_file.save(
                    name=f"schema_{cur_release.tag}.json",
                    content=open(json_file, "rb"),
                )
