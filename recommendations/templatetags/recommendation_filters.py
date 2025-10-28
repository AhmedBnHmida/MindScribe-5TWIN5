"""
Custom template filters for recommendations module.
"""
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument.
    Usage: {{ value|multiply:100 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Divide the value by the argument.
    Usage: {{ value|divide:total }}
    """
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """
    Calculate percentage.
    Usage: {{ count|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

