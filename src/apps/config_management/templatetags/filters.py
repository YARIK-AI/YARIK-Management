from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(name="get_name_by_key")
def get_name_by_key(value, arg):
    if isinstance(arg, SafeString):
        return value[arg].name


@register.filter(name="get_desc_by_key")
def get_desc_by_key(value, arg):
    if isinstance(arg, SafeString):
        return value[arg].description