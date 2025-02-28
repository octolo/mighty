from django.urls import include, path

from mighty.applications.messenger import views

app_name = 'messenger'
urlpatterns = [
    path('messenger/', include([
        path('email/viewer/<uuid:uid>/', views.EmailViewer.as_view(), name='messenger-email-viewer'),
    ])),
]

wbh_urlpatterns = [
    path('messenger/', include([
        path('email/', views.WebhookMessenger.as_view(), name='wbh-messenger-email'),
        path('emailar/', views.WebhookEmailAR.as_view(), name='wbh-messenger-emailar'),
        path('postal/', views.WebhookPostal.as_view(), name='wbh-messenger-postal'),
        path('postalar/', views.WebhookPostalAR.as_view(), name='wbh-messenger-postalar'),
        path('sms/', views.WebhookSMS.as_view(), name='wbh-messenger-sms'),
        path('web/', views.WebhookWeb.as_view(), name='wbh-messenger-web'),
        path('app/', views.WebhookApp.as_view(), name='wbh-messenger-app'),
    ])),
]
