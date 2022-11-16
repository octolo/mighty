from django.urls import path, include
from mighty.applications.messenger import views
from mighty.functions import setting

app_name = 'messenger'
urlpatterns = [
    path('messenger/', include([
        path('email/viewer/<uuid:uid>/', views.EmailViewer.as_view(), name="messenger-email-viewer"),
        path('email/confirm/<uuid:uid>/', views.EmailService.confirm_email_read, name="messenger-email-confirm-read")
    ])),
]

if 'oauth2_provider' in setting('INSTALLED_APPS'):
    wbh_urlpatterns = [
        path('messenger/', include([
            path('email/', views.WebhookMessenger.as_view(), name="wbh-messenger-email"),
            path('emailar/', views.WebhookEmailAR.as_view(), name="wbh-messenger-emailar"),
            path('postal/', views.WebhookPostal.as_view(), name="wbh-messenger-postal"),
            path('postalar/', views.WebhookPostalAR.as_view(), name="wbh-messenger-postalar"),
            path('sms/', views.WebhookSMS.as_view(), name="wbh-messenger-sms"),
            path('web/', views.WebhookWeb.as_view(), name="wbh-messenger-web"),
            path('app/', views.WebhookApp.as_view(), name="wbh-messenger-app"),
        ])),
    ]