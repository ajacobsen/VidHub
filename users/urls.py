from django.urls import path, re_path

from . import views as users_views

app_name = 'users'
urlpatterns = [
	path("signup/", users_views.SignupView.as_view(), name="signup"),
	path('login/', users_views.LoginView.as_view(), name="login"),
	path("logout/", users_views.LogoutView.as_view(), name="users_logout"),
	re_path(r'^(?P<key>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', users_views.ActivateView.as_view(), name='activate'),
]