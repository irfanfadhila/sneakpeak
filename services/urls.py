__author__ = 'irfan'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^getDosen/$', views.getDosen, name='getDosen'),
]