# products/templatetags/product_tags.py
from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split a string by a delimiter and return a list."""
    return value.split(delimiter)

@register.filter
def in_list(value, the_list):
    return value in the_list