from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry

import urllib
import json

# action_flag = {1: "insert", 2: "update", 3: "delete", 4: "view"}

# Create your views here.
@login_required()
def index(request):
    cursor = 'home'

    data = {'results': []}
    try:
        url = "http://sidang.int.cs.ui.ac.id:8017/services/history_bimbingan"
        response = urllib.urlopen(url)
        data = json.load(response)
    except (ValueError, IOError) as e:
        print 'No service found'

    count_skripsi = 0
    count_ka = 0
    count_proptesis = 0
    count_usulpltn = 0
    count_pltns3 = 0
    count_prapromosi = 0
    count_calons3 = 0
    count_promosi = 0
    count_tesis = 0
    count_lain = 0

    for d in data['results']:
        if d['jenis'] == 'skripsi':
            count_skripsi += 1
        elif d['jenis'] == 'karya akhir':
            count_ka += 1
        elif d['jenis'] == 'proposal thesis':
            count_proptesis += 1
        elif d['jenis'] == 'usulan penelitian':
            count_usulpltn += 1
        elif d['jenis'] == 'seminar hasil penelitian S3':
            count_pltns3 += 1
        elif d['jenis'] == 'pra promosi':
            count_prapromosi += 1
        elif d['jenis'] == 'wawancara calon S3':
            count_calons3 += 1
        elif d['jenis'] == 'promosi':
            count_promosi += 1
        elif d['jenis'] == 'thesis':
            count_tesis += 1
        else:
            count_lain += 1

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="home",
        action_flag=4,
        change_message="membuka halaman home",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'adminsdm/index.html', {'cursor': cursor,
                                                   'count_skripsi': count_skripsi,
                                                   'count_ka': count_ka,
                                                   'count_proptesis': count_proptesis,
                                                   'count_usulpltn': count_usulpltn,
                                                   'count_pltns3': count_pltns3,
                                                   'count_prapromosi': count_prapromosi,
                                                   'count_calons3': count_calons3,
                                                   'count_promosi': count_promosi,
                                                   'count_tesis': count_tesis,
                                                   'count_lain': count_lain})

@login_required()
def profilpegawai(request):
    cursor = 'profil'

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="profil pegawai",
        action_flag=4,
        change_message="membuka halaman profil pegawai",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'profilpegawai/index.html', {'cursor': cursor})

@login_required()
def profildetail(request):
    cursor = 'profil'

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="profil detail",
        action_flag=4,
        change_message="membuka halaman profil detail",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'profilpegawai/profil_detail.html', {'cursor': cursor})

@login_required()
def angkakredit(request):
    cursor = 'angk'

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="angka kredit",
        action_flag=4,
        change_message="membuka halaman angka kredit",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'angkakredit/index.html', {'cursor': cursor})

@login_required()
def logactivity(request):
    cursor = 'log'
    log = LogEntry.objects.all()
    return render(request, 'logactivity/index.html', {'cursor': cursor, 'log': log})
