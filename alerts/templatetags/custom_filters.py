from django import template

register = template.Library()

@register.filter
def remove_underscores(value):
    """
    Replace underscores with spaces and capitalize words.
    Example: "water_level" becomes "Water Level"
    
    * reference: https://docs.djangoproject.com/en/4.2/ref/templates/builtins/
    """
    if isinstance(value, str):
        return value.replace('_', ' ').title()
    return value