from django.urls import path

from . import views

app_name = 'testlog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('http_status', views.HttpStatusView.as_view(), name='http_status'),
    path('http_status_line', views.HttpStatusLineView.as_view(), name='http_status_line'),
    path('inner_ip', views.InnerIPView.as_view(), name='inner_ip'),
    path('inner_ip_ip', views.InnerIPIPView.as_view(), name='inner_ip_ip'),
    path('outer_ip', views.OuterIPView.as_view(), name='outer_ip'),
    path('outer_ip_ip', views.OuterIPIPView.as_view(), name='outer_ip_ip'),
    path('user_agent_browser', views.UserAgentBrowserView.as_view(), name='user_agent_browser'),
]
