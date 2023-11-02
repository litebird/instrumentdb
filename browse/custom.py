# -*- encoding: utf-8 -*-

"""
This file enables the user to customize the appearance of several views.

The way it is supposed to be used is the following:

1. Fork the repository https://github.com/ziotom78/instrumentdb

2. Modify the HTML templates for the views you want to personalize (they are in
   browse/templates/)

3. Modify this file so that you provide context variables useful for the templates
   you personalized in step #2. You should usually start by getting an instance
   of the object that is being displayed, e.g., with the line

       cur_release = context["object"].tag

   in `create_release_view_context`

4. You can substitute the file browse/static/browse/logo.svg with your own logo

5. Deploy your fork using a webserver!
"""
from typing import Any

import json


# This is used to prepare the context for the template
# borwse/templates/browse/entity_detail.html
# The field context["object"] is the instance the Entity class
def create_entity_view_context(context):
    """Create the context to render a :class:`EntityListView`"""
    pass


# This is used to prepare the context for the template
# borwse/templates/browse/quantity_detail.html
# The field context["object"] is the instance the Quantity class
def create_quantity_view_context(context):
    """Create the context to render a :class:`QuantityView`"""
    pass


# This is used to prepare the context for the template
# borwse/templates/browse/datafile_detail.html
# The field context["object"] is the instance the DataFile class
def create_datafile_view_context(context):
    """Create the context to render a :class:`DataFileView`"""
    pass


def extract_info_from_metadata(
    quantities,
    release_tag: str,
    quantity_name: str,
    uuid_field_name: str,
    result: dict[Any, Any],
):
    quantity = quantities.get(name=quantity_name)
    scanning_obj = quantity.data_files.get(release_tags__tag=release_tag)
    result[uuid_field_name] = scanning_obj.uuid

    return json.loads(scanning_obj.metadata)


# This is used to prepare the context for the template
# borwse/templates/browse/release_detail.html
# The field context["object"] is the instance the Release class
def create_release_view_context(context):
    """Create the context to render a :class:`ReleaseView`"""

    from django.core.exceptions import ObjectDoesNotExist
    from browse.models import Entity

    release_tag = context["object"].tag

    # We must check if we're running a test or the full webserver for LiteBIRD
    # Let's assume that we're in the latter case if there is an entity called
    # "satellite", one called "LFT", one called "MFT", and one called "HFT"
    try:
        observation = (
            Entity.objects.get(level=0, name="PLM")
            .get_children()
            .get(name="Observation")
        )
        instruments = {
            "lft": Entity.objects.get(level=0, name="LFT"),
            "mft": Entity.objects.get(level=0, name="MFT"),
            "hft": Entity.objects.get(level=0, name="HFT"),
        }

        context["litebird_flag"] = True

        # Scanning strategy
        scanning_metadata = extract_info_from_metadata(
            quantities=observation.quantities,
            release_tag=release_tag,
            quantity_name="Scanning_Strategy",
            uuid_field_name="scanning_uuid",
            result=context,
        )

        for key in (
            "spin_sun_angle_deg",
            "precession_period_min",
            "spin_rate_rpm",
        ):
            context[key] = scanning_metadata.get(key, 0)

        observation_time_metadata = extract_info_from_metadata(
            quantities=observation.quantities,
            release_tag=release_tag,
            quantity_name="Observation_Time",
            uuid_field_name="observation_time_uuid",
            result=context,
        )

        for key in (
            "mission_duration_year",
            "observation_duty_cycle",
            "cosmic_ray_loss",
            "margin",
        ):
            context[key] = observation_time_metadata.get(key, 0)

        # Channels
        context["instruments"] = []
        for instr_name, instr_entity in instruments.items():
            channels = []
            for channel_entity in (
                instr_entity.get_children()
                .get(name="Frequency_Channels")
                .get_children()
            ):
                channel_quantity = channel_entity.quantities.get(name="channel_info")
                channel_obj = channel_quantity.data_files.get(
                    release_tags__tag=context["object"].tag
                )
                channel_metadata = json.loads(channel_obj.metadata)
                channel_dict = {
                    "name": channel_entity.name,
                    "uuid": channel_obj.uuid,
                }
                for key in (
                    "bandcenter_ghz",
                    "bandwidth_ghz",
                    "number_of_detectors",
                    "net_detector_ukrts",
                    "net_channel_ukrts",
                    "pol_sensitivity_detector_ukarcmin",
                    "pol_sensitivity_channel_ukarcmin",
                ):
                    channel_dict[key] = channel_metadata.get(key, 0)

                channels.append(channel_dict)

            context["instruments"].append(
                {
                    "name": instr_name,
                    "channels": channels,
                }
            )
    except ObjectDoesNotExist:
        context["litebird_flag"] = False


# This is used to prepare the context for the template
# borwse/templates/browse/release_list.html
def create_release_listview_context(context):
    """Create the context to render a :class:`ReleaseListView`"""
    pass
