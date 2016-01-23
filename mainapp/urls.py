from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^accounts/login$', 'django_cas_ng.views.login'),
    url(r'^accounts/logout$', 'django_cas_ng.views.logout'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/login/'}, name='logout'),
    url(r'^authFailed/$', views.authFailed, name='views.authFailed'),
    url(r'^local/$', views.local, name='views.local'),
    #url(r'^manual/$', views.manual, name='manual'),
]