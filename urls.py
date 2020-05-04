from django.conf import settings

app_name = "mighty"
urlpatterns = []

# Enable app nationality
if "mighty.applications.nationality" in settings.INSTALLED_APPS:
    from mighty.applications.nationality import urls as urls_nationality
    urlpatterns += urls_nationality.urlpatterns

# Enable app user
if "mighty.applications.user" in settings.INSTALLED_APPS:
    from mighty.applications.user.urls import urlpatterns as urls_user
    urlpatterns += urls_user

# Enable app twofactor
if "mighty.applications.twofactor" in settings.INSTALLED_APPS:
    from mighty.applications.twofactor.urls import urlpatterns as urls_twofactor
    urlpatterns += urls_twofactor

# Enable app grapher
if "mighty.applications.grapher" in settings.INSTALLED_APPS:
    from mighty.applications.grapher.urls import urlpatterns as urls_grapher
    urlpatterns += urls_grapher