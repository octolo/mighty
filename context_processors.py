from django.conf import settings
from django.utils.module_loading import import_string
from mighty.translates import templates as _

# Generate menus from the MIGHTY_BACKOFFICE setting
def menus(request):
    if hasattr(settings, "MIGHTY_BACKOFFICE"): 
        return {"applications": {label: [import_string(model)() for model in models] for label,models in settings.MIGHTY_BACKOFFICE.items()}}

# Add additionnal value in all context
def additionnal(request):
    if hasattr(settings, "CONTEXT_ADD"): 
        return {"additional": settings.CONTEXT_ADD}

# Add debug setting in all context
def debug(request):
    return {"debug": settings.DEBUG}

# Add translates in all context
def translate(request):
    return {
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
