from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * arg

@register.filter
def split(value, arg):
    """Split a string into a list based on the argument"""
    return value.split(arg)
