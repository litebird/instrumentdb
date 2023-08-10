# -*- encoding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase
from browse.models import Entity, Quantity, DataFile, FormatSpecification


class RelationshipsTestCase(TestCase):
    def setUp(self):
        # Structure of the objects in this test case:
        #
        # Focal plane: "rtc_focal_plane" (entity)
        #  |
        #  +--> Beam: "rtc_beam" (entity)
        #       |
        #       +--> GRASP beam: "rtc_grasp_beam" (quantity)
        #       |    |
        #       |    +--> GRASP file: "rtc_grasp_beam.fits" (data file)
        #       |
        #       +--> Synthetic beam: "rtc_synth_beam" (quantity)
        #            |
        #            +--> JSON file: "rtc_synth_beam.json" (data file)

        fp = Entity.objects.create(name="rtc_focal_plane", parent=None)
        beam = Entity.objects.create(name="rtc_beam", parent=fp)
        grasp_spec = FormatSpecification.objects.create(
            document_ref="RTC-DOC-REF-001",
            title="GRASP beam file definition",
            file_mime_type="application/fits",
        )
        synth_spec = FormatSpecification.objects.create(
            document_ref="RTC-DOC-REF-002",
            title="Synthetic beam file definition",
            file_mime_type="application/json",
        )

        grasp_beam = Quantity.objects.create(
            name="rtc_grasp_beam", format_spec=grasp_spec, parent_entity=beam
        )
        synth_beam = Quantity.objects.create(
            name="rtc_synth_beam", format_spec=synth_spec, parent_entity=beam
        )

        grasp_file = DataFile.objects.create(
            name="rtc_grasp_beam.fits",
            quantity=grasp_beam,
            spec_version="1.0",
        )

        synth_file = DataFile.objects.create(
            name="rtc_synth_beam.json",
            metadata="{'fwhm_deg': 1.0}",
            quantity=synth_beam,
            spec_version="2.0",
        )

        # Mark the synthetic beam as a derived product of the GRASP beam
        synth_file.dependencies.add(grasp_file)

    def test_entities(self):
        fp = Entity.objects.get(name="rtc_focal_plane")
        beam = Entity.objects.get(name="rtc_beam")

        assert not fp.parent  # The focal plane has no parent
        assert beam.parent == fp

    def test_quantities(self):
        beam = Entity.objects.get(name="rtc_beam")
        grasp_beam = Quantity.objects.get(name="rtc_grasp_beam")
        synth_beam = Quantity.objects.get(name="rtc_synth_beam")
        assert grasp_beam.parent_entity == beam
        assert synth_beam.parent_entity == beam
        assert grasp_beam.format_spec != synth_beam.format_spec
        assert (
            grasp_beam.format_spec.document_ref != synth_beam.format_spec.document_ref
        )

    def test_bad_names(self):
        with self.assertRaises(ValidationError):
            Entity.name.field.run_validators(value="wrong name with spaces")

        with self.assertRaises(ValidationError):
            Quantity.name.field.run_validators(value="wrong name with spaces")

    def test_data_files(self):
        grasp_beam = Quantity.objects.get(name="rtc_grasp_beam")
        synth_beam = Quantity.objects.get(name="rtc_synth_beam")
        grasp_file = DataFile.objects.get(name="rtc_grasp_beam.fits")
        synth_file = DataFile.objects.get(name="rtc_synth_beam.json")

        assert grasp_file.quantity == grasp_beam
        assert synth_file.quantity == synth_beam

        assert grasp_file.dependencies.count() == 0

        assert synth_file.dependencies.count() == 1
        assert synth_file.dependencies.all()[0] == grasp_file
