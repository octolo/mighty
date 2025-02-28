from django.urls import include, path

from mighty.applications.twofactor import views

app_name = 'twofactor'
urlpatterns = []
api_urlpatterns = [
    path('twofactor/', include([
        path('form/', include([
            path('login/', views.TwoFactorSearchFormDesc.as_view(), name='api-form-desc-login'),
            path('choice/', views.TwoFactorChoicesFormDesc.as_view(), name='api-form-desc-choice'),
            path('code/', views.TwoFactorCodeFormDesc.as_view(), name='api-form-desc-code'),
        ])),
        path('sendcode/', views.APISendCode.as_view())
    ])),
]
