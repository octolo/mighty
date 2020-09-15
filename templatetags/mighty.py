from django import template
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.urls import reverse
import datetime

register = template.Library()

guardian = False
if 'guardian' in settings.INSTALLED_APPS:
    from guardian.core import ObjectPermissionChecker
    guardian = True

"""
Simple tag
"""

@register.simple_tag(name='has_perm')
def has_perm(obj, user, perm):
    if hasattr(obj, 'perm'):
        return ObjectPermissionChecker(user).has_perm(perm, obj) if guardian else user.has_perm(obj.perm(perm))
    else:
        return False

@register.simple_tag(name='verbose_name')
def verbose_name(obj):
    return obj._meta.verbose_name

@register.simple_tag(name='verbose_name_plural')
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural

@register.simple_tag(name='field_name')
def field_name(obj, field):
    if field == '__str__':
        return obj._meta.verbose_name
    else:
        try:
            return obj._meta.get_field(field).verbose_name
        except FieldDoesNotExist:
            try:
                return getattr(obj, field).short_description
            except Exception:
                pass
    return ""

@register.simple_tag(name='field_value')
def field_value(obj, field):
    if field == '__str__':
        return str(obj)
    else:
        attr = getattr(obj, field)
    attr = attr() if callable(attr) else attr
    return None if attr is None else attr

@register.simple_tag(name='add_attr')
def add_attr(field, attr, value):
    return field.as_widget(attrs={attr: value})

@register.simple_tag(name='number_hread')
def number_hread(number, separator=None):
    return '{:,}'.format(int(number)).replace(",", separator) if separator else '{:,}'.format(int(number))

@register.simple_tag(name='is_type')
def is_type(data):
    return type(data).__name__.lower()

@register.simple_tag(name='define')
def define(val=None):
  return val

@register.simple_tag(name='convert_date')
def convert_date(date, origin, convert):
    return datetime.datetime.strptime(date, origin).strftime(convert)

"""
Filter based templatetag
"""

@register.filter(name='add_attrs')
def add_attrs(field, css):
    attrs = {}
    definition = css.split(',')
    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            key, val = d.split(':')
            attrs[key] = val
    return field.as_widget(attrs=attrs)

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def indexkey(dct, key):
    return dct.get(key)

@register.filter(name='split')
def split(value, key):
  return value.split(key)

@register.filter(name='has_m2m')
def has_m2m(m2mfield, m2m, field='id'):
    m2m_id = int(getattr(m2m, field))
    return m2mfield.filter(**{field: m2m_id}).count()

from django.contrib.contenttypes.models import ContentType

@register.filter(name='contenttype_id')
def contenttype_id(model):
    try:
        return ContentType.objects.get(app_label=model._meta.app_label, model=model._meta.model_name).id
    except ContentType.DoesNotExist:
        return