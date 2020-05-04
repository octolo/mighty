from django.contrib import admin
from mighty.models.applications.nationality import Nationality
from mighty.applications.nationality.admin import NationalityAdmin

@admin.register(Nationality)
class NationalityAdmin(NationalityAdmin):
    pass