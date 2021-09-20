from django.conf import settings
from django.urls import path, include
from mighty.applications.shop import views

app_name='shop'
urlpatterns = [
    path('shop/', include([
        path('invoice/<uuid:uid>/', include([
            path('pdf/', views.ShopInvoicePDF.as_view(), name="pdf")
        ])),
    ])),
]
api_urlpatterns = [
    path('shop/', include([
        path('bic/', views.BicCalculJSON.as_view()),
        path('form/', include([
            path('cb/', views.CBFormDescView.as_view()),
            path('iban/', views.IbanFormDescView.as_view()),
            path('paymentmethod/', views.PaymentMethodFormDescView.as_view()),
        ])),
        path('check/', include([
            path('cb/', views.CheckCB.as_view()),
            path('iban/', views.CheckIban.as_view()),
        ])),
    ])),
]

