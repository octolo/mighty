from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

tpls = {
    "javascript": """<script type='text/javascript' %(async)s src="%(src)s"></script>""",
    "stylesheet": """<link rel="stylesheet" href="%(href)s">""",
}

@register.simple_tag(name='external_lib')
def external_lib(libtype):
    libext = settings.MIGHTY_LIBEXT
    libs = libext.get(libtype)
    if libs:
        tpl = tpls.get(libtype)
        html = ""
        for lib in libs:
            html+=tpl % (lib)
    return mark_safe(html)
