# D:\Django\bhavi_fashion (2)\bhavi_fashion\templatetags\admin_tags.py
from django import template

register = template.Library()

@register.filter
def lookup(obj, key):
    """
    Dynamically look up an attribute or method result on an object.
    """
    try:
        # Handle callable attributes (e.g., methods like product_count)
        value = getattr(obj, key)
        if callable(value):
            return value()
        return value
    except (AttributeError, TypeError):
        return ''