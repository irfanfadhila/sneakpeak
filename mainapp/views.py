from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_cas_ng.signals import cas_user_authenticated
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('mainapp:login'))
    # elif request.user.groups.filter(name="mahasiswa"):
    #   return HttpResponseRedirect(reverse('lowongan:listLowongan'))
    elif request.user.groups.filter(name="administrator"):
        return HttpResponseRedirect(reverse('adminsdm:index'))
    # elif request.user.groups.filter(name="sekretariat"):
    #	return HttpResponseRedirect(reverse('log:listLogByDate'))
    # elif request.user.groups.filter(name="dosen"):
    #	return HttpResponseRedirect(reverse('administrasi:listLowongan'))
    else:
        return render(request, 'mainapp/index.html')

def authFailed(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('mainapp:login'))
    return render(request, 'mainapp/authFailed.html')

def local(request):
    return render(request, 'mainapp/loginlocal.html')
