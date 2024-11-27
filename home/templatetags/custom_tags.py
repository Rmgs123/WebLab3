# home/templatetags/custom_tags.py
from django import template
import bleach

register = template.Library()

@register.filter(name='sanitize')
def sanitize(value):
    allowed_tags = ['b', 'i', 'u']
    allowed_attrs = {}

    return bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)
