from django.contrib import admin
from mighty.models.applications.twofactor import Twofactor
from mighty.applications.twofactor.admin import TwofactorAdmin

@admin.register(Twofactor)
class TwofactorAdmin(TwofactorAdmin):
    pass