from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('http', views.http_view, name='http'),
    path('http/<int:log_id>', views.http_details, name='http_details'),
    path('http/down/<int:log_id>', views.download_http_body, name='download_http_body'),
    path('dns', views.dns_view, name='dns'),
    path('xss', views.xss_view, name='xss'),
    path('file', views.file_service_view, name='file'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('delete/http', views.delete_http_record, name='delete_http_record'),
    path('delete/dns', views.delete_dns_record, name='delete_dns_record'),

    re_path('.*', views.handle_http_request, name='http_request_handler'),
]
