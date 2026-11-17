# -*- encoding: utf-8 -*-

# See the Django docs to understand how this works:
# https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/

import json

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def format_json(value):
    try:
        d = json.loads(value)
        return json.dumps(d, indent=4)
    except json.JSONDecodeError:
        pass

    return value

@register.filter
def metadata_items(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []

    if isinstance(value, dict):
        return value.items()

    return []


@register.filter
def display_metadata_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return value
