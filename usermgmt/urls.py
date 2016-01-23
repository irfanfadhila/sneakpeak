from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^createUser/$', views.createUser, name='createUser'),
    url(r'^viewUser/(?P<id>[0-9]+)/$', views.viewUser, name='viewUser'),
    url(r'^editUser/(?P<id>[0-9]+)/$', views.editUser, name='editUser'),
    url(r'^deleteUser/(?P<id>[0-9]+)/$', views.deleteUser, name='deleteUser'),
    url(r'^createPermission/$', views.createPermission, name='createPermission'),
    url(r'^viewPermission/(?P<id>[0-9]+)/$', views.viewPermission, name='viewPermission'),
    url(r'^editPermission/(?P<id>[0-9]+)/$', views.editPermission, name='editPermission'),
    url(r'^createGroupPerm/$', views.createGroupPerm, name='createGroupPerm'),
    url(r'^viewGroupPerm/(?P<id>[0-9]+)/$', views.viewGroupPerm, name='viewGroupPerm'),
    url(r'^editGroupPerm/(?P<id>[0-9]+)/$', views.editGroupPerm, name='editGroupPerm'),
    url(r'^createUserPerm/$', views.createUserPerm, name='createUserPerm'),
    url(r'^viewUserPerm/(?P<id>[0-9]+)/$', views.viewUserPerm, name='viewUserPerm'),
    url(r'^editUserPerm/(?P<id>[0-9]+)/$', views.editUserPerm, name='editUserPerm'),
]
