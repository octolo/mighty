from django.urls import path, include

from mighty.applications.twofactor import views
urlpatterns = [path('twofactor/', include(views.TwofactorViewSet().urls)),]
loginviews = [path("", views.Login.as_view(), name="login"),]
loginviews.append(path("basic/<uid>", views.LoginBasic.as_view(), name="login-basic"))
loginviews.append(path("email/<uid>", views.LoginEmail.as_view(), name="login-email"))
loginviews.append(path("sms/<uid>", views.LoginSms.as_view(), name="login-sms"))
loginviews.append(path("logout/", views.Logout.as_view(), name="logout"))
urlpatterns.append(path('login/', include(loginviews)))