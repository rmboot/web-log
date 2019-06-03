from django.urls import path

from . import views

app_name = 'logtest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('today_access', views.TodayAccessView.as_view(), name='today_access'),
    path('recent_log_table', views.RecentLogView.as_view(), name='recent_log_table'),
    path('err_log_table', views.ErrLogView.as_view(), name='err_log_table'),
    path('http_status_pie', views.HttpStatusPieView.as_view(), name='http_status_pie'),
    path('http_status_line', views.HttpStatusLineView.as_view(), name='http_status_line'),
    path('inner_ip', views.InnerIPView.as_view(), name='inner_ip'),
    path('inner_diff_ip', views.InnerDiffIPView.as_view(), name='inner_diff_ip'),
    path('outer_ip', views.OuterIPView.as_view(), name='outer_ip'),
    path('outer_diff_ip', views.OuterDiffIPView.as_view(), name='outer_diff_ip'),
    path('ua_browser_bot', views.UABrowserBotView.as_view(), name='ua_browser_bot'),
    path('ua_browser_detail', views.UABrowserDetailView.as_view(), name='ua_browser_detail'),
    path('ua_os', views.UAOsView.as_view(), name='ua_os'),
]
