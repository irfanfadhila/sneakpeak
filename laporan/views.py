__author__ = 'irfan'

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.contrib.admin.models import LogEntry
# import mysql.connector
import json
import urllib
import requests
from django.http import HttpResponse

@login_required()
def index(request):
    cursor = 'laporan'
    data_sidang = get_laporan_sisidang()
    data_siak = get_laporan_siak()

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="laporan",
        action_flag=4,
        change_message="membuka halaman laporan",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'laporan/index.html', {'data_sidang': data_sidang, 'data_siak': data_siak, 'cursor': cursor})

def get_laporan_sisidang():
    try:
        url = "http://sidang.int.cs.ui.ac.id:8017/services/history_bimbingan"
        response = urllib.urlopen(url)
        data = json.load(response)
        return data
    except (ValueError, IOError) as e:
        print 'No service found'
        return

def get_laporan_siak():
    try:
        url = "https://apps.cs.ui.ac.id/webservice/dosen_mk.php?term=1&tahun=2014"
        r = requests.get(url)
        return r.json()
    except (ValueError, TypeError) as e:
        print 'No service found'
        return
