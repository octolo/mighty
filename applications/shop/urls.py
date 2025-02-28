from django.urls import include, path

from mighty.applications.shop import views

app_name = 'shop'

urlpatterns = [
    path('shop/', include([
        path('bill/', include([
            path('<uuid:uid>/pdf/', views.BillPDF.as_view(), name='bill-pdf')
        ])),
    ])),
]
api_urlpatterns = [
    path('shop/', include([
        path('bic/', views.BicCalculJSON.as_view(), name='pm-bic'),
        path('form/', include([
            path('cb/', views.CBFormDescView.as_view(), name='form-cb'),
            path('iban/', views.IbanFormDescView.as_view(), name='form-iban'),
            path('paymentmethod/', views.PaymentMethodFormDescView.as_view(), name='pm-form'),
            path('frequency/', views.FrequencyFormDescView.as_view(), name='pm-form'),
        ])),
        path('check/', include([
            path('cb/', views.CheckCB.as_view(), name='check-cb'),
            path('iban/', views.CheckIban.as_view(), name='check-iban'),
        ])),
        path('bill/', include([
            path('<uuid:uid>/list/', views.BillList.as_view(), name='bill-list')
        ])),
    ])),
]

webhooks_urlpatterns = [
    path('shop/', include([
        path('stripe/', include([
            path('checkstatus/<str:payment_id>/', views.StripeCheckStatus.as_view(), name='stripe-check-status'),
        ])),
    ])),
]
