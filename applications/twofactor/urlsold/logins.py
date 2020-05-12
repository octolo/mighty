from django.urls import path, include
from mighty.applications.twofactor import views

app_name='twofactor'
urlpatterns = [path("", views.Login.as_view(), name="login"),]
urlpatterns.append(path("basic/<uid>", views.LoginBasic.as_view(), name="login-basic"))
urlpatterns.append(path("email/<uid>", views.LoginEmail.as_view(), name="login-email"))
urlpatterns.append(path("sms/<uid>", views.LoginSms.as_view(), name="login-sms"))
urlpatterns.append(path("logout/", views.Logout.as_view(), name="logout"))