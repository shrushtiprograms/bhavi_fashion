# accounts/templatetags/admin_extras.py
from django import template
register = template.Library()

@register.filter(name='get_attribute')  # Changed name
def get_attribute(obj, attr):
    try:
        value = obj.__getattribute__(attr)  # Using __getattribute__ instead
        return value() if callable(value) else value
    except AttributeError:
        return None