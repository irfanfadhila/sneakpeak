from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^profilpegawai/$', views.profilpegawai, name='profilpegawai'),
    url(r'^profildetail/$', views.profildetail, name='profildetail'),
    url(r'^angkakredit/$', views.angkakredit, name='angkakredit'),
    url(r'^logactivity/$', views.logactivity, name='logactivity'),
]
