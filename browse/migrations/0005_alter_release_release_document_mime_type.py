# Generated by Django 4.2.4 on 2023-08-08 10:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("browse", "0004_alter_release_release_document"),
    ]

    operations = [
        migrations.AlterField(
            model_name="release",
            name="release_document_mime_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("text/plain", "Plain text"),
                    ("text/html", "HTML"),
                    ("application/pdf", "Adobe PDF"),
                    ("text/rtf", "Rich-Text Format (.rtf)"),
                    ("text/markdown", "Markdown"),
                    ("application/x-abiword", "AbiWord document"),
                    ("application/msword", "Microsoft Word (.doc)"),
                    (
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "Microsoft Word (.docx)",
                    ),
                    ("application/vnd.amazon.ebook", "Amazon Kindle eBook"),
                    ("application/epub+zip", "Electronic publication (EPUB)"),
                    (
                        "application/vnd.oasis.opendocument.text",
                        "OpenDocument text document (.odt)",
                    ),
                    (
                        "application/vnd.oasis.opendocument.presentation",
                        "OpenDocument presentation document (.odp)",
                    ),
                    (
                        "application/vnd.oasis.opendocument.spreadsheet",
                        "OpenDocument spreadsheet document (.ods)",
                    ),
                    ("application/vnd.ms-powerpoint", "Microsoft PowerPoint (.ppt)"),
                    (
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "Microsoft PowerPoint (.pptx)",
                    ),
                    ("application/vnd.ms-excel", "Microsoft Excel (.xls)"),
                    (
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "Microsoft Excel (.xlsx)",
                    ),
                    ("application/octet-stream", "Other (unknown)"),
                ],
                default="text/plain",
                help_text="This specifies the MIME type of the downloadable copy of the release document",
                max_length=256,
                null=True,
                verbose_name="MIME type of the specification document",
            ),
        ),
    ]
