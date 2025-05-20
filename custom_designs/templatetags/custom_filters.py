from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replaces all occurrences of the first string with the second in the argument"""
    if not value or not arg:
        return value
    old, new = arg.split(',')
    return value.replace(old, new)