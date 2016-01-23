__author__ = 'Irfan'

from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

class UserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50, required=False)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(label='First Name', max_length=100, required=False)
    last_name = forms.CharField(label='Last Name', max_length=100, required=False)
    role = forms.ModelChoiceField(label='Choose Role', queryset=Group.objects.all(), required=False)

class PermissionForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    content_type = forms.ModelChoiceField(label='Choose Content Type', queryset=ContentType.objects.all())
    codename = forms.CharField(label='Codename', max_length=100)

class GpermForm(forms.Form):
    group = forms.ModelChoiceField(label='Group', queryset=Group.objects.all())
    perm = forms.ModelChoiceField(label='Permission', queryset=Permission.objects.all())

class UpermForm(forms.Form):
    user = forms.ModelChoiceField(label='User', queryset=User.objects.all())
    perm = forms.ModelChoiceField(label='Permission', queryset=Permission.objects.all())