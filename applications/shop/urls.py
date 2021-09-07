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
        path('bic/', views.BicCalculJSON.as_view())
    ])),
]

