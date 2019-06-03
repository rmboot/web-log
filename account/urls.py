from django.conf.urls import url
from django.contrib.auth import views as auth_view

from . import views
from .forms import LoginForm

app_name = "account"

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(success_url='/'), name='login', kwargs={'authentication_form': LoginForm}),
    url(r'^register/$', views.RegisterView.as_view(success_url="/"), name='register'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout')
]