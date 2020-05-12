from django.conf import settings
from django.utils.module_loading import import_string
from mighty import translates as _

# Generate menus from the MIGHTY_BACKOFFICE setting
def menus(request):
    if hasattr(settings, "MIGHTY_BACKOFFICE"): 
        return {"applications": {label: [import_string(model)() for model in models] for label,models in settings.MIGHTY_BACKOFFICE.items()}}

# Add translates in all context
def mighty(request):
    return {
        "additional": settings.CONTEXT_ADD if hasattr(settings, "CONTEXT_ADD") else {},
        "logo": settings.LOGO_STATIC if hasattr(settings, "LOGO_STATIC") else "img/django.svg",
        "debug": settings.DEBUG,
        "mighty": {
            "home": _.home,
            "login": _.login,
            "logout": _.logout,
            "admin": _.admin,
            "admin_view": _.admin_view,
            "nc": _.nc,
            "next": _.next,
            "previous": _.previous
        }
    }
