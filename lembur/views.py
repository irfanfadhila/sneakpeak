from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from .models import Lembur, Pegawai, JenisLembur, StatusLembur, KomponenLembur, Jabatan, UnitKerja, PermissionLembur
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date, time, timedelta, datetime
from django.utils import timezone
import urllib
import requests
import json
import locale
from django.db.models import Q
import calendar
# start untuk pdf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Rect
from io import BytesIO
from easy_pdf.views import PDFTemplateView
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
# end untuk pdf
# action_flag = {1: "insert", 2: "update", 3: "delete", 4: "view"}

# Create your views here.
@login_required()
def index(request):
    cursor = 'lembur'
    try:
        pegawai = Pegawai.objects.get(user_id=request.user.id)
    except Exception as e:
        print(e)
        pegawai = None
    return render(request, "lembur/index.html", {'pegawai': pegawai, 'cursor': cursor})

@login_required()
def lembur(request, ket):
    try:
        pegawai = Pegawai.objects.get(user_id=request.user.id)
    except Exception as e:
        return index(request)
    cursor = ket
    if ket == "pegawai":
        lembursaya = Lembur.objects.filter(pegawai_id__user_id=request.user.id, created_by_id__user_id=request.user.id)
        return render(request, "lembur/pegawai.html",
                      {'lembur': True,
                       'pegawai': True,
                       'cursor': cursor,
                       'lembursaya': lembursaya})
    elif ket == "pembayaranlembur":
        harikerja = Lembur.objects.filter(jenis_lembur_id=3, status_id=9, pegawai_id__user_id=request.user.id)
        harilibur = Lembur.objects.filter(jenis_lembur_id=4, status_id=9, pegawai_id__user_id=request.user.id)
        return render(request, "lembur/pembayaranlembur.html",
                      {'lembur': True,
                       'pegawai': True,
                       'cursor': cursor,
                       'harikerja': harikerja,
                       'harilibur': harilibur})
    elif ket == "manager":
        manager = Pegawai.objects.get(user_id=request.user.id)
        if manager.permission.id != 3 and pegawai.permission.id != 1:
            return index(request)
        persetujuanlembur = Lembur.objects.filter(pegawai_id__unit_id=manager.unit.id, status_id=7)
        return render(request, "lembur/manager.html",
                      {'lembur': True,
                       'cursor': cursor,
                       'manager': manager,
                       'persetujuanlembur': persetujuanlembur})
    elif ket == "lemburunit":
        manager = Pegawai.objects.get(user_id=request.user.id)
        if manager.permission.id != 3 and pegawai.permission.id != 1:
            return index(request)
        lemburunit = Lembur.objects.filter(pegawai_id__unit_id=manager.unit.id)
        return render(request, "lembur/lemburunit.html",
                      {'lembur': True,
                       'cursor': cursor,
                       'manager': manager,
                       'lemburunit': lemburunit})
    elif ket == "piclembur":
        piclembur = Pegawai.objects.get(user_id=request.user.id)
        if piclembur.permission.id != 2 and pegawai.permission.id != 1:
            return index(request)
        arrunit = []
        unit = UnitKerja.objects.all()
        for u in unit:
            count = Lembur.objects.filter(pegawai_id__unit_id=u.id, status_id=8).count()
            tuppleunit = {'id': u.id, 'unit': u.unit, 'count': count}
            arrunit.append(tuppleunit)
        lemburverifikasi = Lembur.objects.filter(status_id=8)
        return render(request, "lembur/piclembur.html",
                      {'lembur': True,
                       'piclembur': True,
                       'cursor': cursor,
                       'lemburverifikasi': lemburverifikasi,
                       'arrunit': arrunit})
    elif ket == "pembayaranselesai":
        piclembur = Pegawai.objects.get(user_id=request.user.id)
        if piclembur.permission.id != 2 and pegawai.permission.id != 1:
            return index(request)
        lemburpembayaran = Lembur.objects.filter(status_id=9)
        lemburselesai = Lembur.objects.filter(status_id=10)
        return render(request, "lembur/pembayaranselesai.html",
                      {'lembur': True,
                       'piclembur': True,
                       'cursor': cursor,
                       'lemburpembayaran': lemburpembayaran,
                       'lemburselesai': lemburselesai})
    elif ket == "laporankeuangan":
        piclembur = Pegawai.objects.get(user_id=request.user.id)
        if piclembur.permission.id != 2 and pegawai.permission.id != 1:
            return index(request)
        return render(request, "lembur/laporankeuangan.html",
                      {'lembur': True,
                       'piclembur': True,
                       'cursor': cursor})
    elif ket == "keuanganperminggu":
        piclembur = Pegawai.objects.get(user_id=request.user.id)
        if piclembur.permission.id != 2 and pegawai.permission.id != 1:
            return index(request)
        return render(request, "lembur/keuanganperminggu.html",
                      {'lembur': True,
                       'piclembur': True,
                       'cursor': cursor})
    elif ket == "master":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdpegawai = Pegawai.objects.all()
        selectjabatan = Jabatan.objects.all()
        selectunit = UnitKerja.objects.all()
        selectpermission = PermissionLembur.objects.all()
        return render(request, "lembur/master/mdpegawai.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdpegawai': mdpegawai,
                       'selectjabatan': selectjabatan,
                       'selectunit': selectunit,
                       'selectpermission': selectpermission})
    elif ket == "masterjabatan":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdjabatan = Jabatan.objects.all()
        return render(request, "lembur/master/mdjabatan.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdjabatan': mdjabatan})
    elif ket == "masterjenis":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdjenis = JenisLembur.objects.all()
        return render(request, "lembur/master/mdjenis.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdjenis': mdjenis})
    elif ket == "masterkomponen":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdkomponen = KomponenLembur.objects.all()
        selectjabatan = Jabatan.objects.all()
        return render(request, "lembur/master/mdkomponen.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdkomponen': mdkomponen,
                       'selectjabatan': selectjabatan})
    elif ket == "masterlembur":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdlembur = Lembur.objects.all()
        selectstatus = StatusLembur.objects.all()
        selectjenis = JenisLembur.objects.all()
        return render(request, "lembur/master/mdlembur.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdlembur': mdlembur,
                       'selectstatus': selectstatus,
                       'selectjenis': selectjenis})
    elif ket == "masterstatus":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdstatus = StatusLembur.objects.all()
        return render(request, "lembur/master/mdstatus.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdstatus': mdstatus})
    elif ket == "masterunit":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdunit = UnitKerja.objects.all()
        return render(request, "lembur/master/mdunit.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdunit': mdunit})
    elif ket == "masterpermission":
        admin = Pegawai.objects.get(user_id=request.user.id)
        if admin.permission.id != 1:
            return index(request)
        mdpermission = PermissionLembur.objects.all()
        return render(request, "lembur/master/mdpermission.html",
                      {'lembur': True,
                       'master': True,
                       'cursor': cursor,
                       'mdpermission': mdpermission})
    else:
        return render(request, "lembur/index.html")

@login_required()
def ajukanlembur(request):
    print("kesini")
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            pegawai = Pegawai.objects.get(user_id=result['pegawai'])
            tanggal = result['tanggal']
            jenis = JenisLembur.objects.get(id=3)
            if 'jenis' in result:
                jenis = JenisLembur.objects.get(id=4)
            deskripsi = result['deskripsi']
            mulai = result['mulai']
            selesai = result['selesai']
            status = StatusLembur.objects.get(id=6)
            if result['ajukan'] == 'ajukan':
                status = StatusLembur.objects.get(id=7)
            lastmodified = timezone.now()
            #crated_by = Pegawai.objects.get(user_id=request.user.id)
            #lastmodified_by = Pegawai.objects.get(user_id=request.user.id)
            lembur = Lembur(
                pegawai_id=pegawai.id, tanggal=tanggal, jenis_lembur_id=jenis.id, deskripsi_pekerjaan=deskripsi,
                waktu_mulai=mulai, waktu_selesai=selesai, status_id=status.id, last_modified=lastmodified,
                created_by_id=pegawai.id, last_modified_by_id=pegawai.id
            )
            print(result)
            try:
                lembur.save()
                success = {
                    'lembur': lembur.id, 'deskripsi': lembur.deskripsi_pekerjaan, 'tanggal': lembur.tanggal,
                    'mulai': lembur.waktu_mulai, 'selesai': lembur.waktu_selesai, 'status': lembur.status.status
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as f:
                print(f)
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def ajukanlemburmanager(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            manager = Pegawai.objects.get(user_id=request.user.id)
            lastmodified = timezone.now()
            status = StatusLembur.objects.get(id=6)
            if result['ajukan'] == 'ajukan':
                status = StatusLembur.objects.get(id=8)
            deskripsi = result['deskripsi']
            mulai = result.getlist('mulai')
            selesai = result.getlist('selesai')
            jenis = result.getlist('jenis')
            tanggal = result.getlist('tanggal')
            pegawai = result.getlist('pegawai')
            try:
                success = []
                for x in tanggal:
                    counter = 0
                    jenislembur = JenisLembur.objects.get(id=3)
                    if jenis[counter] == 1:
                        jenislembur = JenisLembur.objects.get(id=4)
                    for y in pegawai:
                        lembur = Lembur(
                            pegawai_id=y, tanggal=x, jenis_lembur_id=jenislembur.id, deskripsi_pekerjaan=deskripsi,
                            waktu_mulai=mulai[counter], waktu_selesai=selesai[counter], status_id=status.id, last_modified=lastmodified,
                            created_by_id=manager.id, last_modified_by_id=manager.id
                        )
                        lembur.save()
                        element = {
                            'lembur': lembur.id, 'deskripsi': lembur.deskripsi_pekerjaan, 'tanggal': lembur.tanggal,
                            'mulai': lembur.waktu_mulai, 'selesai': lembur.waktu_selesai, 'status': lembur.status.status,
                            'pegawai': lembur.pegawai.user.first_name, 'created': lembur.created_by.user.first_name
                        }
                        success.append(element)
                    counter += 1
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def lihatlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            lembur = Lembur.objects.get(id=request.POST['lembur'])
            pegawai = lembur.pegawai.id
            namapegawai = lembur.pegawai.user.first_name
            deskripsi = lembur.deskripsi_pekerjaan
            tanggal = lembur.tanggal
            jenis = False
            if lembur.jenis_lembur.id == 4:
                jenis = True
            mulai = lembur.waktu_mulai
            selesai = lembur.waktu_selesai
            status = lembur.status.id
            createdby = User.objects.get(id=lembur.created_by.user.id)
            success = {
                'lembur': lembur.id, 'pegawai': pegawai, 'namapegawai': namapegawai, 'deskripsi': deskripsi,
                'tanggal': tanggal, 'jenis': jenis, 'mulai': mulai, 'selesai': selesai, 'status': status,
                'createdby': createdby.id, 'request': request.user.id, 'masuk': lembur.waktu_masuk,
                'keluar': lembur.waktu_keluar, 'bantuan': lembur.bantuan, 'makan': lembur.makan,
                'transport': lembur.transport
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def ubahlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            print(result)
            lembur = Lembur.objects.get(id=result['lembur'])
            if result['pegawai'] != lembur.pegawai:
                lembur.pegawai = Pegawai.objects.get(id=result['pegawai'])
            if result['deskripsi'] != lembur.deskripsi_pekerjaan:
                lembur.deskripsi_pekerjaan = result['deskripsi']
            if result['tanggal'] != lembur.tanggal:
                lembur.tangal = result['tanggal']
            if result['mulai'] != lembur.waktu_mulai:
                lembur.waktu_mulai = result['mulai']
            if result['selesai'] != lembur.waktu_selesai:
                lembur.waktu_selesai = result['selesai']
            if 'jenis' in result and lembur.jenis_lembur.id == 3:
                lembur.jenis_lembur = JenisLembur.objects.get(id=4)
            if result['ajukan'] == 'ajukan':
                lembur.status = StatusLembur.objects.get(id=7)
            elif result['ajukan'] == 'ajukanmanager':
                lembur.status = StatusLembur.objects.get(id=8)
            elif result['ajukan'] == 'tolak':
                lembur.status = StatusLembur.objects.get(id=6)
            elif result['ajukan'] == 'setujui':
                lembur.status = StatusLembur.objects.get(id=8)
            elif result['ajukan'] == 'verifikasi':
                lembur.status = StatusLembur.objects.get(id=9)
                lembur.waktu_masuk = result['masuk']
                lembur.waktu_keluar = result['keluar']
                lembur.bantuan = result['bantuan']
                lembur.makan = result['makan']
                lembur.transport = result['transport']
            elif result['ajukan'] == 'pembayaran':
                lembur.status = StatusLembur.objects.get(id=10)
            lastmodified = timezone.now()
            lastmodified_by = Pegawai.objects.get(user_id=request.user.id)
            if lembur.last_modified_by != lastmodified_by.id:
                lembur.last_modified_by = lastmodified_by
                lembur.last_modified = lastmodified
            try:
                lembur.save()
                success = {
                    'lembur': lembur.id, 'deskripsi': lembur.deskripsi_pekerjaan, 'tanggal': lembur.tanggal,
                    'mulai': lembur.waktu_mulai, 'selesai': lembur.waktu_selesai, 'status': lembur.status.status,
                    'namapegawai': lembur.pegawai.user.first_name, 'createdby': lembur.created_by.user.first_name,
                    'unitid': lembur.pegawai.unit.id, 'jenis': lembur.jenis_lembur.jenis_lembur
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as f:
                print(f)
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def hapuslembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            lembur = result['lembur']
            dellembur = Lembur.objects.get(id=lembur)
            if dellembur.status.id == 6:
                try:
                    dellembur.delete()
                    success = {
                        'lembur': lembur
                    }
                    print(json.dumps(success, cls=DjangoJSONEncoder))
                    return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
                except Exception as e:
                    print(e)
            else:
                print('gagal')
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def caripegawai(request):
    try:
        if request.is_ajax():
            term = request.GET.get('term', '')
            manager = Pegawai.objects.get(user_id=request.user.id)
            if manager.id == 24:
                pegawai = Pegawai.objects.filter(user_id__first_name__icontains=term)[:20]
            elif request.user.is_superuser:
                pegawai = Pegawai.objects.filter(user_id__first_name__icontains=term)[:20]
            else:
                pegawai = Pegawai.objects.filter(user_id__first_name__icontains=term, unit_id=manager.unit)[:20]
            pegawaiarr = []
            for p in pegawai:
                pegawaijson = {'id': p.id, 'value': p.id, 'label': p.user.first_name + ' ' + p.user.last_name}
                pegawaiarr.append(pegawaijson)
            return HttpResponse(json.dumps(pegawaiarr), content_type='application/json')
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def cariuser(request):
    try:
        if request.is_ajax():
            term = request.GET.get('term', '')
            user = User.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term))[:20]
            userarr = []
            for u in user:
                userjson = {'id': u.id, 'value': u.id, 'label': u.first_name + ' ' + u.last_name}
                userarr.append(userjson)
            return HttpResponse(json.dumps(userarr), content_type='application/json')
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def cekabsen(request):
    try:
        if request.is_ajax():
            result = request.POST
            username = Pegawai.objects.get(id=result['username'])
            print(username.user.username)
            print(result)
            try:
                url = "https://apps.cs.ui.ac.id/webservice/absensi.php?username="+ str(username.user.username) +"&tanggal="+ str(result['tanggal'])
                r = requests.get(url)
                # return r.json()
                # url = "https://apps.cs.ui.ac.id/webservice/absensi.php?username=aji.nursyamsi&tanggal=2015-10-10"
                # response = urllib.urlopen(url)
                # data = json.load(response)
                data = r.json()
                print(data)
                success = {
                    'masuk': data['jam_datang'], 'keluar': data['jam_pulang']
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except (ValueError, IOError) as e:
                print 'No service found'
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def formharikerja(request, id):
    cursor = 'pembayaranlembur'
    lemburform = Lembur.objects.get(id=id)
    if lemburform.pegawai.user.id != request.user.id:
        return index(request)
    masuk_h = lemburform.waktu_masuk.hour
    masuk_m = lemburform.waktu_masuk.minute
    keluar_h = lemburform.waktu_keluar.hour
    kelur_m = lemburform.waktu_keluar.minute
    waktu_h = keluar_h - masuk_h
    waktu_m = kelur_m - masuk_m
    if waktu_m < 0:
        waktu_h -= 1
        waktu_m += 60
    komponenlembur = KomponenLembur.objects.filter(jabatan_id=lemburform.pegawai.jabatan.id)
    bantuan = int(komponenlembur[0].besaran) * int(waktu_h)
    makan = 0
    if waktu_h >= 2:
        makan = komponenlembur[1].besaran
    transport = 0
    manajer = Pegawai.objects.get(jabatan_id=14, unit_id=lemburform.pegawai.unit.id)
    return render(request, "lembur/formharikerja.html",
                  {'lembur': True,
                   'pegawai': True,
                   'cursor': cursor,
                   'lemburform': lemburform,
                   'waktu_h': waktu_h,
                   'waktu_m': waktu_m,
                   'bantuan': bantuan,
                   'makan': makan,
                   'transport': transport,
                   'manajer': manajer})

@login_required()
def formharilibur(request, id):
    cursor = 'pembayaranlembur'
    lemburform = Lembur.objects.get(id=id)
    if lemburform.pegawai.user.id != request.user.id:
        return index(request)
    hariini = timezone.now()
    return render(request, "lembur/formharilibur.html",
                  {'lembur': True,
                   'pegawai': True,
                   'cursor': cursor,
                   'lemburform': lemburform,
                   'hariini': hariini})

@login_required()
def pdfharikerja(request, id):
    lembur = Lembur.objects.get(id=id)
    if lembur.pegawai.user.id != request.user.id:
        return index(request)
    nama = lembur.pegawai.user.first_name + " " + lembur.pegawai.user.last_name
    hari = lembur.tanggal.strftime("%w")
    hariindo = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
    for x in range(0, 7):
        print(x)
        if x == int(hari):
            hari = hariindo[x]
            break
    tanggal = lembur.tanggal.strftime("%d %B %Y")
    pukul = lembur.waktu_mulai.strftime("%H:%M") + " - " + lembur.waktu_selesai.strftime("%H:%M")
    deskripsi = lembur.deskripsi_pekerjaan
    jam = lembur.waktu_masuk.strftime("%H:%M") + " - " + lembur.waktu_keluar.strftime("%H:%M")
    masuk_h = lembur.waktu_masuk.hour
    masuk_m = lembur.waktu_masuk.minute
    keluar_h = lembur.waktu_keluar.hour
    kelur_m = lembur.waktu_keluar.minute
    waktu_h = keluar_h - masuk_h
    waktu_m = kelur_m - masuk_m
    if waktu_m < 0:
        waktu_h -= 1
        waktu_m += 60
    waktu = str(waktu_h) + " jam " + str(waktu_m) + " menit"
    komponenlembur = KomponenLembur.objects.filter(jabatan_id=lembur.pegawai.jabatan.id)
    bantuan = int(komponenlembur[0].besaran) * int(waktu_h)
    if waktu_h >= 2:
        makan = komponenlembur[1].besaran
    transport = 0
    manajer = Pegawai.objects.get(jabatan_id=14, unit_id=lembur.pegawai.unit.id)
    nama_manajer = manajer.user.first_name + " " + manajer.user.last_name
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="laporanharikerja.pdf"'
    buff = BytesIO()
    p = canvas.Canvas(buff, pagesize=A4)
    p.drawImage('/home/irfan/PycharmProjects/sisdmcs/sisdmcs/static/image/fasilkom-merah-biru.jpg', 50, 730, width=70, height=70)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(150, 770, "Fakultas Ilmu Komputer")
    p.drawString(160, 740, "Universitas Indonesia")
    p.setFont("Helvetica-Bold", 16)
    p.drawString(240, 680, "TUGAS LEMBUR")
    p.setFont("Helvetica", 12)
    p.drawString(50, 650, "Diperintahkan")
    p.drawString(50, 630, "Nama")
    p.drawString(150, 630, ":")
    p.drawString(160, 630, nama)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 600, "Untuk melaksanakan tugas lembur pada")
    p.setFont("Helvetica", 12)
    p.drawString(50, 570, "Hari")
    p.drawString(150, 570, ":")
    p.drawString(160, 570, hari)
    p.drawString(50, 550, "Tanggal")
    p.drawString(150, 550, ":")
    p.drawString(160, 550, tanggal)
    p.drawString(50, 530, "Ditugaskan pukul")
    p.drawString(150, 530, ":")
    p.drawString(160, 530, pukul)
    p.drawString(50, 510, "Yang dikerjakan")
    p.drawString(150, 510, ":")
    p.drawString(160, 510, deskripsi)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 480, "Surat tugas lembur ini diserahkan setelah ditanda tangani lengkap")
    p.rect(50, 430, 495, 30)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(230, 440, "DIISI OLEH BAGIAN SDM")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 400, "Telah dilaksanakan")
    p.drawString(50, 380, "Tanggal")
    p.setFont("Helvetica", 12)
    p.drawString(150, 380, ":")
    p.drawString(160, 380, tanggal)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 360, "Jam")
    p.setFont("Helvetica", 12)
    p.drawString(150, 360, ":")
    p.drawString(160, 360, jam)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 340, "Waktu")
    p.setFont("Helvetica", 12)
    p.drawString(150, 340, ":")
    p.drawString(160, 340, waktu)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 310, "Bantuan")
    p.setFont("Helvetica", 12)
    p.drawString(150, 310, ":")
    p.drawString(160, 310, "Rp " + str(bantuan) + ",00")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 290, "Makan")
    p.setFont("Helvetica", 12)
    p.drawString(150, 290, ":")
    p.drawString(160, 290, "Rp " + str(makan) + ",00")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 270, "Transport")
    p.setFont("Helvetica", 12)
    p.drawString(150, 270, ":")
    p.drawString(160, 270, "Rp " + str(transport) + ",00")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(270, 220, "Mengetahui")
    p.drawString(100, 180, "Pelaksana Kerja")
    p.drawString(410, 180, "Pemberi Tugas")
    p.setFont("Helvetica", 12)
    p.drawString(100, 100, "(" + nama + ")")
    p.drawString(400, 100, "(" + nama_manajer + ")")
    p.showPage()
    p.save()
    pdf = buff.getvalue()
    buff.close()
    response.write(pdf)
    return response

@login_required()
def pdfharilibur(request, id):
    lembur = Lembur.objects.get(id=id)
    if lembur.pegawai.user.id != request.user.id:
        return index(request)
    deskripsi = lembur.deskripsi_pekerjaan
    pegawai = lembur.pegawai.user.first_name + " " + lembur.pegawai.user.last_name
    hari = lembur.tanggal.strftime("%w")
    hariindo = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
    for x in range(0, 7):
        print(x)
        if x == int(hari):
            hari = hariindo[x]
            break
    tanggal = lembur.tanggal.strftime("%d %B %Y")
    pukul = lembur.waktu_mulai.strftime("%H:%M") + " s.d " + lembur.waktu_selesai.strftime("%H:%M")
    tempat = lembur.tempat
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="laporanharikerja.pdf"'

    doc = SimpleDocTemplate(response,pagesize=A4,
                        rightMargin=60,leftMargin=60,
                        topMargin=60,bottomMargin=18)
    Story=[]

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=18))
    styles.add(ParagraphStyle(name='Tab', leftIndent=24))
    styles.add(ParagraphStyle(name='TabFooter', leftIndent=270))

    header = '<font size=12><b>%s</b></font>' % "SURAT TUGAS"
    Story.append(Paragraph(header, styles['Center']))
    Story.append(Spacer(1, 6))

    header = '<font size=12>%s</font>' % "735.A/UN2.F11.D2.SF2/OTL.03.SuratTugas/2015"
    Story.append(Paragraph(header, styles['Center']))
    Story.append(Spacer(1, 12))

    header = '<font size=12>%s</font>' % deskripsi
    Story.append(Paragraph(header, styles['Center']))
    Story.append(Spacer(1, 6))

    header = '<font size=12>%s</font>' % "Depok, " + timezone.now().strftime("%d %B %Y")
    Story.append(Paragraph(header, styles['Center']))
    Story.append(Spacer(1, 36))

    isi = '<font size=12>%s</font>' % "Yang bertanda tangan dibawah ini:"
    Story.append(Paragraph(isi, styles['Normal']))
    Story.append(Spacer(1, 18))

    isi = '<font size=12>Nama &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : Dra. Kasiyah, M.Sc.</font>'
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 6))

    isi = '<font size=12>Jabatan &nbsp;&nbsp; : Wakil Dekan Bidang Sumber Daya, Ventura dan Administrasi Umum</font>'
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 6))

    isi = '<font size=12>NIP &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : 196105101987032001</font>'
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 18))

    isi = '<font size=12>Dengan ini menugaskan kepada <b>%s</b> untuk <b>%s</b> yang akan dilaksanakan pada:</font>' % (pegawai, deskripsi)
    Story.append(Paragraph(isi, styles['Justify']))
    Story.append(Spacer(1, 18))

    isi = '<font size=12>Hari/Tanggal &nbsp; : %s</font>' % hari + ", " + tanggal
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 6))

    isi = '<font size=12>Waktu &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : %s</font>' % pukul
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 6))

    isi = '<font size=12>Tempat &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : %s</font>' % tempat
    Story.append(Paragraph(isi, styles['Tab']))
    Story.append(Spacer(1, 18))

    isi = '<font size=12>Demikian Surat Tugas ini dibuat untuk dapat dipergunakan sebagaimana mestinya.</font>'
    Story.append(Paragraph(isi, styles['Justify']))
    Story.append(Spacer(1, 42))

    footer = '<font size=12>%s</font>' % "Depok, " + timezone.now().strftime("%d %B %Y")
    Story.append(Paragraph(footer, styles['TabFooter']))
    Story.append(Spacer(1, 18))

    footer = '<font size=12>Wakil Dekan Bidang Sumber Daya, Ventura dan Administrasi Umum</font>'
    Story.append(Paragraph(footer, styles['TabFooter']))
    Story.append(Spacer(1, 72))

    footer = '<font size=12><b>Dra. Kasiyah, M.Sc.</b></font>'
    Story.append(Paragraph(footer, styles['TabFooter']))
    Story.append(Spacer(1, 6))

    footer = '<font size=12>NIP. 196105101987032001</font>'
    Story.append(Paragraph(footer, styles['TabFooter']))
    Story.append(Spacer(1, 6))

    doc.build(Story)
    return response

@login_required()
def cariperiode(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            term = request.POST
            periode_mulai = term['periode_mulai']
            periode_selesai = term['periode_selesai']
            lembur = Lembur.objects.filter(status_id=9, tanggal__range=[periode_mulai, periode_selesai])
            lemburarr = []
            listuser = []
            for l in lembur:
                uname = l.pegawai.user.username
                nama = l.pegawai.user.first_name + " " + l.pegawai.user.last_name
                bantuan = l.bantuan
                makan = l.makan
                transport = l.transport
                if uname in listuser:
                    for la in lemburarr:
                        if la['uname'] == uname:
                            la['lembur'] += bantuan
                            la['makan'] += makan
                            la['transport'] += transport
                else:
                    listuser.append(uname)
                    lemburjson = {'uname': uname, 'nama': nama, 'lembur': bantuan, 'makan': makan, 'transport': transport}
                    lemburarr.append(lemburjson)
            return HttpResponse(json.dumps(lemburarr), content_type='application/json')
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def pdflaporanperiode(request):
    locale.setlocale(locale.LC_ALL, '')
    result = request.POST
    periode_mulai = result['p_start']
    periode_selesai = result['p_end']
    per_mulai = datetime.strptime(periode_mulai, "%Y-%m-%d")
    per_selesai = datetime.strptime(periode_selesai, "%Y-%m-%d")
    periode = per_mulai.strftime("%d %B") + ' - ' + per_selesai.strftime("%d %B %Y")
    lembur = Lembur.objects.filter(status_id=9, tanggal__range=[periode_mulai, periode_selesai])
    lemburarr = []
    listuser = []
    for l in lembur:
        uname = l.pegawai.user.username
        nama = l.pegawai.user.first_name + " " + l.pegawai.user.last_name
        bantuan = l.bantuan
        makan = l.makan
        transport = l.transport
        if uname in listuser:
            for la in lemburarr:
                if la['uname'] == uname:
                    la['lembur'] += bantuan
                    la['makan'] += makan
                    la['transport'] += transport
        else:
            listuser.append(uname)
            lemburjson = {'uname': uname, 'nama': nama, 'lembur': bantuan, 'makan': makan, 'transport': transport}
            lemburarr.append(lemburjson)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="laporanperiode.pdf"'

    doc = SimpleDocTemplate(response,pagesize=landscape(A4),
                        rightMargin=60,leftMargin=60,
                        topMargin=40,bottomMargin=18)
    Story = []

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=18))
    styles.add(ParagraphStyle(name='Tab', leftIndent=24))
    styles.add(ParagraphStyle(name='TabFooter', leftIndent=500))

    header = '<font size=12><b>%s</b></font>' % "Daftar Lembur Pegawai"
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 6))

    header = '<font size=12><b>%s</b></font>' % "Fasilkom UI"
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 12))

    header = '<font size=12><b>%s</b></font>' % "Periode: " + periode
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 36))

    no = Paragraph('<b>No.</b>', styles['Center'])
    nama = Paragraph('<b>Nama</b>', styles['Center'])
    bantuan = Paragraph('<b>Lembur</b>', styles['Center'])
    makan = Paragraph('<b>U.Makan</b>', styles['Center'])
    transport = Paragraph('<b>Transport</b>', styles['Center'])
    total = Paragraph('<b>Total</b>', styles['Center'])
    ttd = Paragraph('<b>Tanda Tangan</b>', styles['Center'])

    data = [
        [no, nama, bantuan, makan, transport, total, ttd, '']
    ]

    height = [None]

    countlembur = 0
    countmakan = 0
    counttransport = 0
    counttotal = 0

    count = 1
    for dl in lemburarr:
        total = dl['lembur'] + dl['makan'] + dl['transport']
        angka = Paragraph('<super>%s</super>' % count, styles['Left'])
        if count % 2 == 0:
            dtmp = [count, dl['nama'],
                    locale.currency(dl['lembur'], grouping=True),
                    locale.currency(dl['makan'], grouping=True),
                    locale.currency(dl['transport'], grouping=True),
                    locale.currency(total, grouping=True), '', angka]
        else:
            dtmp = [count, dl['nama'],
                    locale.currency(dl['lembur'], grouping=True),
                    locale.currency(dl['makan'], grouping=True),
                    locale.currency(dl['transport'], grouping=True),
                    locale.currency(total, grouping=True), angka, '']
        data.append(dtmp)
        height.append(40)
        countlembur += dl['lembur']
        countmakan += dl['makan']
        counttransport += dl['transport']
        counttotal += total
        count += 1

    totalT = Paragraph('<b>Total</b>', styles['Left'])
    footer = ['', totalT,
              locale.currency(countlembur, grouping=True),
              locale.currency(countmakan, grouping=True),
              locale.currency(counttransport, grouping=True),
              locale.currency(counttotal, grouping=True), '', '']
    data.append(footer)
    height.append(None)

    t = Table(data, colWidths=[30, 150, None, None, None, None, None, None], rowHeights=height, style=[
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (-2,0), (-1,0)),
        ('VALIGN', (-2,0), (-1,-1), 'TOP')
    ])

    Story.append(t)
    Story.append(Spacer(1, 72))

    footer = '<font size=12>Mengetahui,</font>'
    Story.append(Paragraph(footer, styles['Tab']))
    Story.append(Spacer(1, 12))

    footer = '<font size=12>Manajer Umum,</font>' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '<font size=12>Asisten Manajer Bidang SDM,</font>'
    Story.append(Paragraph(footer, styles['Tab']))
    Story.append(Spacer(1, 72))

    footer = '<font size=12><b>Dr. Indra Budi</b></font>' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
             '<font size=12><b>Hennie Marianie</b></font>'
    Story.append(Paragraph(footer, styles['Tab']))
    Story.append(Spacer(1, 6))

    doc.build(Story)

    return response

@login_required()
def cariperminggu(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            term = request.POST
            print(term)
            lemburarr = []
            pegawai = term['pegawai']
            if int(term['brpminggu']) == 0:
                today = date.today()
            else:
                yglalu = 7 * int(term['brpminggu'])
                today = date.today() - timedelta(days=yglalu)
            if today.weekday() == 0:
                carimulai = today
                cariselesai = today + timedelta(days=6)
            elif today.weekday() == 6:
                cariselesai = today
                carimulai = today - timedelta(days=6)
            else:
                x = today.weekday() - 6
                y = 6 + x
                carimulai = today - timedelta(days=y)
                cariselesai = today + timedelta(days=abs(x))
            print(carimulai)
            print(cariselesai)
            hari = {0: ['Senin', carimulai],
                    1: ['Selasa', carimulai + timedelta(days=1)],
                    2: ['Rabu', carimulai + timedelta(days=2)],
                    3: ['Kamis', carimulai + timedelta(days=3)],
                    4: ['Jumat', carimulai + timedelta(days=4)],
                    5: ['Sabtu', carimulai + timedelta(days=5)],
                    6: ['Minggu', cariselesai]}
            jmlwaktutotal = 0
            jmlwaktudec = ''
            jmlmakan = 0
            jmltransport = 0
            jmluanglembur = 0
            jmluangmakan = 0
            jmluangtransport = 0
            namapegawai = Pegawai.objects.get(id=pegawai)
            for x in range(0, 7):
                lembur = Lembur.objects.filter(pegawai_id=pegawai, status_id=9, tanggal=hari[x][1])
                if lembur:
                    jammasuk = (int(lembur[0].waktu_masuk.strftime("%H")) * 100)
                    menitmasuk = int(lembur[0].waktu_masuk.strftime("%M"))
                    jamkeluar = (int(lembur[0].waktu_keluar.strftime("%H")) * 100)
                    menitkeluar = int(lembur[0].waktu_keluar.strftime("%M"))
                    jamdikurangi = jamkeluar - jammasuk
                    menitdikurangi = menitkeluar - menitmasuk
                    menit = menitdikurangi
                    durasi1 = jamdikurangi + menit
                    if menitdikurangi < 0:
                        menit = (60 - menitkeluar) + (60 - menitmasuk)
                        jamdikurangi = jamdikurangi - 100
                        durasi1 = jamdikurangi + menit
                    jammulai = (int(lembur[0].waktu_mulai.strftime("%H")) * 100)
                    menitmulai = int(lembur[0].waktu_mulai.strftime("%M"))
                    jamselesai = (int(lembur[0].waktu_selesai.strftime("%H")) * 100)
                    menitselesai = int(lembur[0].waktu_selesai.strftime("%M"))
                    jdikurang = jamselesai - jammulai
                    mdikurang = menitselesai - menitmulai
                    minute = mdikurang
                    durasi2 = jdikurang - minute
                    if mdikurang < 0:
                        minute = (60 - menitselesai) + (60 - menitmulai)
                        jdikurang = jdikurang - 100
                        durasi2 = jdikurang + minute
                    jmlwaktu = durasi1 - durasi2
                    if jmlwaktu % 100 != 0 and durasi2 > durasi1:
                        jmlwaktu = jmlwaktu + 40
                    jmlwaktutotal = jmlwaktutotal + durasi1
                    stringmenit = str(jmlwaktutotal)[2:]
                    if stringmenit is not '':
                        intmenit = float(stringmenit)
                        decmenit = (intmenit / 60) * 100
                        jmlwaktudec = str(jmlwaktutotal)[:2] + ',' + str(int(decmenit))
                    if durasi1 >= 200:
                        jmlmakan = jmlmakan + 1
                    if lembur[0].jenis_lembur.id == 4:
                        jmltransport = jmltransport + 1
                    jmluanglembur = jmluanglembur + lembur[0].bantuan
                    jmluangmakan = jmluangmakan + lembur[0].makan
                    jmluangtransport = jmluangtransport + lembur[0].transport
                    jsonresult = {'hari': str(hari[x][0]),
                                  'tanggal': str(lembur[0].tanggal),
                                  'masuk': str(lembur[0].waktu_masuk),
                                  'keluar': str(lembur[0].waktu_keluar),
                                  'wkthadir': str(jamdikurangi/100) + ' : ' + str(menit),
                                  'wktlembur': str(jamdikurangi/100) + ' : ' + str(menit),
                                  'jmlwaktu': jmlwaktu,
                                  'ket': '',
                                  'jmlwaktutotal': str(jmlwaktutotal)[:2] + ' : ' + str(jmlwaktutotal)[2:],
                                  'jmlwaktudec': jmlwaktudec,
                                  'pegawai': namapegawai.user.first_name + ' ' + namapegawai.user.last_name,
                                  'jenispegawai': namapegawai.jabatan.id,
                                  'jmlmakan': jmlmakan,
                                  'jmltransport': jmltransport,
                                  'jmluanglembur': jmluanglembur,
                                  'jmluangmakan': jmluangmakan,
                                  'jmluangtransport': jmluangtransport}
                else:
                    jsonresult = {'hari': str(hari[x][0]),
                                  'tanggal': str(hari[x][1]),
                                  'masuk': '',
                                  'keluar': '',
                                  'wkthadir': '00 : 00',
                                  'wktlembur': '00 : 00',
                                  'jmlwaktu': '',
                                  'ket': '',
                                  'jmlwaktutotal': str(jmlwaktutotal)[:2] + ' : ' + str(jmlwaktutotal)[2:],
                                  'jmlwaktudec': jmlwaktudec,
                                  'pegawai': namapegawai.user.first_name + ' ' + namapegawai.user.last_name,
                                  'jenispegawai': namapegawai.jabatan.id,
                                  'jmlmakan': jmlmakan,
                                  'jmltransport': jmltransport,
                                  'jmluanglembur': jmluanglembur,
                                  'jmluangmakan': jmluangmakan,
                                  'jmluangtransport': jmluangtransport}
                lemburarr.append(jsonresult)
            print(json.dumps(lemburarr))
            return HttpResponse(json.dumps(lemburarr), content_type='application/json')
        else:
            print('gagal')
    except Exception as e:
        print(e)

@login_required()
def pdflaporanperminggu(request):
    locale.setlocale(locale.LC_ALL, '')

    term = request.POST
    print(term)
    lemburarr = []
    pegawai = term['r_pegawai']
    if int(term['r_brpminggu']) == 0:
        today = date.today()
    else:
        yglalu = 7 * int(term['r_brpminggu'])
        today = date.today() - timedelta(days=yglalu)
    if today.weekday() == 0:
        carimulai = today
        cariselesai = today + timedelta(days=6)
    elif today.weekday() == 6:
        cariselesai = today
        carimulai = today - timedelta(days=6)
    else:
        x = today.weekday() - 6
        y = 6 + x
        carimulai = today - timedelta(days=y)
        cariselesai = today + timedelta(days=abs(x))
    hari = {0: ['Senin', carimulai],
            1: ['Selasa', carimulai + timedelta(days=1)],
            2: ['Rabu', carimulai + timedelta(days=2)],
            3: ['Kamis', carimulai + timedelta(days=3)],
            4: ['Jumat', carimulai + timedelta(days=4)],
            5: ['Sabtu', carimulai + timedelta(days=5)],
            6: ['Minggu', cariselesai]}
    jmlwaktutotal = 0
    jmlwaktudec = ''
    jmlmakan = 0
    jmltransport = 0
    jmluanglembur = 0
    jmluangmakan = 0
    jmluangtransport = 0
    namapegawai = Pegawai.objects.get(id=pegawai)
    for x in range(0, 7):
        lembur = Lembur.objects.filter(pegawai_id=pegawai, status_id=9, tanggal=hari[x][1])
        if lembur:
            jammasuk = (int(lembur[0].waktu_masuk.strftime("%H")) * 100)
            menitmasuk = int(lembur[0].waktu_masuk.strftime("%M"))
            jamkeluar = (int(lembur[0].waktu_keluar.strftime("%H")) * 100)
            menitkeluar = int(lembur[0].waktu_keluar.strftime("%M"))
            jamdikurangi = jamkeluar - jammasuk
            menitdikurangi = menitkeluar - menitmasuk
            menit = menitdikurangi
            durasi1 = jamdikurangi + menit
            if menitdikurangi < 0:
                menit = (60 - menitkeluar) + (60 - menitmasuk)
                jamdikurangi = jamdikurangi - 100
                durasi1 = jamdikurangi + menit
            jammulai = (int(lembur[0].waktu_mulai.strftime("%H")) * 100)
            menitmulai = int(lembur[0].waktu_mulai.strftime("%M"))
            jamselesai = (int(lembur[0].waktu_selesai.strftime("%H")) * 100)
            menitselesai = int(lembur[0].waktu_selesai.strftime("%M"))
            jdikurang = jamselesai - jammulai
            mdikurang = menitselesai - menitmulai
            minute = mdikurang
            durasi2 = jdikurang - minute
            if mdikurang < 0:
                minute = (60 - menitselesai) + (60 - menitmulai)
                jdikurang = jdikurang - 100
                durasi2 = jdikurang + minute
            jmlwaktu = durasi1 - durasi2
            if jmlwaktu % 100 != 0 and durasi2 > durasi1:
                jmlwaktu = jmlwaktu + 40
            jmlwaktutotal = jmlwaktutotal + durasi1
            stringmenit = str(jmlwaktutotal)[2:]
            intmenit = float(stringmenit)
            decmenit = (intmenit / 60) * 100
            jmlwaktudec = str(jmlwaktutotal)[:2] + ',' + str(int(decmenit))
            if durasi1 >= 200:
                jmlmakan = jmlmakan + 1
            if lembur[0].jenis_lembur.id == 4:
                jmltransport = jmltransport + 1
            jmluanglembur = jmluanglembur + lembur[0].bantuan
            jmluangmakan = jmluangmakan + lembur[0].makan
            jmluangtransport = jmluangtransport + lembur[0].transport
            jsonresult = {'hari': str(hari[x][0]),
                        'tanggal': str(lembur[0].tanggal),
                        'masuk': str(lembur[0].waktu_masuk),
                        'keluar': str(lembur[0].waktu_keluar),
                        'wkthadir': str(jamdikurangi/100) + ' : ' + str(menit),
                        'wktlembur': str(jamdikurangi/100) + ' : ' + str(menit),
                        'jmlwaktu': jmlwaktu,
                        'ket': '',
                        'jmlwaktutotal': str(jmlwaktutotal)[:2] + ' : ' + str(jmlwaktutotal)[2:],
                        'jmlwaktudec': jmlwaktudec,
                        'pegawai': namapegawai.user.first_name + ' ' + namapegawai.user.last_name,
                        'jenispegawai': namapegawai.jabatan.id,
                        'jmlmakan': jmlmakan,
                        'jmltransport': jmltransport,
                        'jmluanglembur': jmluanglembur,
                        'jmluangmakan': jmluangmakan,
                        'jmluangtransport': jmluangtransport}
        else:
            jsonresult = {'hari': str(hari[x][0]),
                        'tanggal': str(hari[x][1]),
                        'masuk': '',
                        'keluar': '',
                        'wkthadir': '00 : 00',
                        'wktlembur': '00 : 00',
                        'jmlwaktu': '',
                        'ket': '',
                        'jmlwaktutotal': str(jmlwaktutotal)[:2] + ' : ' + str(jmlwaktutotal)[2:],
                        'jmlwaktudec': jmlwaktudec,
                        'pegawai': namapegawai.user.first_name + ' ' + namapegawai.user.last_name,
                        'jenispegawai': namapegawai.jabatan.id,
                        'jmlmakan': jmlmakan,
                        'jmltransport': jmltransport,
                        'jmluanglembur': jmluanglembur,
                        'jmluangmakan': jmluangmakan,
                        'jmluangtransport': jmluangtransport}
        lemburarr.append(jsonresult)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="laporanperiode.pdf"'

    doc = SimpleDocTemplate(response,pagesize=landscape(A4),
                        rightMargin=60,leftMargin=60,
                        topMargin=40,bottomMargin=18)
    Story = []

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=18))
    styles.add(ParagraphStyle(name='Tab', leftIndent=24))
    styles.add(ParagraphStyle(name='TabFooter', leftIndent=500))

    header = '<font size=12><b>%s</b></font>' % "Fakultas Ilmu Komputer - Universitas Indonesia"
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 6))

    header = '<font size=12><b>%s</b></font>' % "Nama Pegawai: " + namapegawai.user.first_name + ' ' + namapegawai.user.last_name
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 24))

    hari = Paragraph('<b>HARI</b>', styles['Center'])
    tanggal = Paragraph('<b>TANGGAL</b>', styles['Center'])
    masuk = Paragraph('<b>JAM MASUK</b>', styles['Center'])
    keluar = Paragraph('<b>JAM KELUAR</b>', styles['Center'])
    hadir = Paragraph('<b>JML WKT HADIR</b>', styles['Center'])
    lembur = Paragraph('<b>JML WKT LEMBUR</b>', styles['Center'])
    waktu = Paragraph('<b>JML WKT +/-</b>', styles['Center'])
    ket = Paragraph('<b>KET.</b>', styles['Center'])

    data = [
        [hari, tanggal, masuk, keluar, hadir, lembur, waktu, ket]
    ]

    ft_count_jmlwkt = ''
    ft_count_jmlwktdec = ''
    count_makan = ''
    count_transport = ''
    count_uanglembur = ''
    count_uangmakan = ''
    count_uangtransport = ''
    for dl in lemburarr:
        dtmp = [dl['hari'], dl['tanggal'], dl['masuk'], dl['keluar'], dl['wkthadir'], dl['wktlembur'],
                dl['jmlwaktu'], dl['ket']]
        ft_count_jmlwkt = dl['jmlwaktutotal']
        ft_count_jmlwktdec = dl['jmlwaktudec']
        count_makan = dl['jmlmakan']
        count_transport = dl['jmltransport']
        count_uanglembur = dl['jmluanglembur']
        count_uangmakan = dl['jmluangmakan']
        count_uangtransport = dl['jmluangtransport']
        data.append(dtmp)

    count_uangtotal = count_uanglembur + count_uangmakan + count_uangtransport

    ft_jmlwkt = Paragraph('<b>JUMLAH WAKTU:</b>', styles['Left'])
    ft_jmlwktdec = Paragraph('<b>Jumlah Waktu (dalam pecahan desimal)</b>', styles['Left'])
    footer = ['', ft_jmlwkt, '', '', ft_count_jmlwkt, ft_count_jmlwkt, '', '']
    data.append(footer)
    footer = ['', ft_jmlwktdec, '', '', ft_count_jmlwktdec, ft_count_jmlwktdec, '', '']
    data.append(footer)

    t = Table(data, style=[
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (1,-1), (3,-1)),
        ('SPAN', (1,-2), (3,-2))
    ])

    Story.append(t)
    Story.append(Spacer(1, 24))

    header = '<font size=12><b>%s</b></font>' % "Jumlah Uang yang Harus Dibayarkan"
    Story.append(Paragraph(header, styles['Left']))
    Story.append(Spacer(1, 24))

    if namapegawai.jabatan.id is 16:
        yuanglembur = '13.000'
        yuangmakan = '25.000'
    else :
        yuanglembur = '17.000'
        yuangmakan = '27.000'
    yuangtransport = '38.000'

    data = [
        ['1.', 'Uang lembur', ':', ft_count_jmlwktdec, 'x', yuanglembur, locale.currency(count_uanglembur, grouping=True)],
        ['2.', 'Uang makan', ':', count_makan, 'x', yuangmakan, locale.currency(count_uangmakan, grouping=True)],
        ['3.', 'Uang transport libur', ':', count_transport, 'x', yuangtransport, locale.currency(count_uangtransport, grouping=True)],
        ['', '', '', '', '', 'JUMLAH', locale.currency(count_uangtotal, grouping=True)]
    ]

    t = Table(data, style=[
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])

    Story.append(t)
    Story.append(Spacer(1, 24))

    footer = '<font size=10><b>Dihitung oleh: (%s)</b></font>' % date.today()
    Story.append(Paragraph(footer, styles['Tab']))
    Story.append(Spacer(1, 72))

    footer = '<font size=10><b>Juwita Ardiana Dwitya</b></font>'
    Story.append(Paragraph(footer, styles['Tab']))
    Story.append(Spacer(1, 6))

    doc.build(Story)

    return response

@login_required()
def mdviewpegawai(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            pegawai = Pegawai.objects.get(id=result['pegawai'])
            permission = ''
            if pegawai.permission != None:
                permission = pegawai.permission.id
            success = {
                'pegawai': pegawai.id, 'nama': pegawai.user.first_name + ' ' + pegawai.user.last_name, 'namaid': pegawai.user.id,
                'nip': pegawai.nip, 'telepon': pegawai.telepon, 'unit': pegawai.unit.id,
                'jabatan': pegawai.jabatan.id, 'permission': permission
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatepegawai(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            pegawai = result['pegawai']
            nip = result['nip']
            telepon = result['telepon']
            unit = result['unit']
            jabatan = result['jabatan']
            permission = result['permission']
            print(result)
            newpegawai = Pegawai(user_id=pegawai, nip=nip, telepon=telepon,
                                        unit_id=unit, jabatan_id=jabatan, permission_id=permission)
            try:
                print('disini')
                newpegawai.save()
                success = {
                    'pegawai': newpegawai.id, 'nama': newpegawai.user.first_name + ' ' + newpegawai.user.last_name,
                    'nip': newpegawai.nip, 'telepon': newpegawai.telepon, 'unit': newpegawai.unit.unit,
                    'jabatan': newpegawai.jabatan.jabatan, 'permission': newpegawai.permission.permission
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditpegawai(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            pegawai = result['pegawai']
            nip = result['nip']
            telepon = result['telepon']
            unit = result['unit']
            jabatan = result['jabatan']
            permission = result['permission']
            editpegawai = Pegawai.objects.get(id=result['idpegawai'])
            editpegawai.user = User.objects.get(id=pegawai)
            editpegawai.nip = nip
            editpegawai.telepon = telepon
            editpegawai.unit = UnitKerja.objects.get(id=unit)
            editpegawai.jabatan = Jabatan.objects.get(id=jabatan)
            editpegawai.permission = PermissionLembur.objects.get(id=permission)
            try:
                editpegawai.save()
                success = {
                    'pegawai': editpegawai.id, 'nama': editpegawai.user.first_name + ' ' + editpegawai.user.last_name,
                    'nip': editpegawai.nip, 'telepon': editpegawai.telepon, 'unit': editpegawai.unit.unit,
                    'jabatan': editpegawai.jabatan.jabatan, 'permission': editpegawai.permission.permission
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletepegawai(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            pegawai = result['idpegawai']
            delpegawai = Pegawai.objects.get(id=pegawai)
            try:
                delpegawai.delete()
                success = {
                    'pegawai': pegawai
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewjabatan(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jabatan = Jabatan.objects.get(id=result['jabatan'])
            success = {
                'jabatan': jabatan.id, 'namajabatan': jabatan.jabatan
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatejabatan(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jabatan = result['jabatan']
            print(result)
            jabatan = Jabatan(jabatan=jabatan)
            try:
                print('disini')
                jabatan.save()
                success = {
                    'jabatan': jabatan.id, 'namajabatan': jabatan.jabatan
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditjabatan(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jabatan = result['jabatan']
            editjabatan = Jabatan.objects.get(id=result['idjabatan'])
            editjabatan.jabatan = jabatan
            try:
                editjabatan.save()
                success = {
                    'jabatan': editjabatan.id, 'namajabatan': editjabatan.jabatan
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletejabatan(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jabatan = result['idjabatan']
            deljabatan = Jabatan.objects.get(id=jabatan)
            try:
                deljabatan.delete()
                success = {
                    'jabatan': jabatan
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewjenislembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jenis = JenisLembur.objects.get(id=result['jenis'])
            success = {
                'jenis': jenis.id, 'jenislembur': jenis.jenis_lembur
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatejenislembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jenis = result['jenis']
            print(result)
            jenislembur = JenisLembur(jenis_lembur=jenis)
            try:
                print('disini')
                jenislembur.save()
                success = {
                    'jenis': jenislembur.id, 'jenislembur': jenislembur.jenis_lembur
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditjenislembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jenis = result['jenis']
            editjenis = JenisLembur.objects.get(id=result['idjenis'])
            editjenis.jenis_lembur = jenis
            try:
                editjenis.save()
                success = {
                    'jenis': editjenis.id, 'jenislembur': editjenis.jenis_lembur
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletejenislembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            jenis = result['idjenis']
            deljenis = JenisLembur.objects.get(id=jenis)
            try:
                deljenis.delete()
                success = {
                    'jenis': jenis
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewkomponenlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            komponen = KomponenLembur.objects.get(id=result['komponen'])
            success = {
                'komponen': komponen.id, 'komponenlembur': komponen.jenis_komponen, 'besaran': komponen.besaran,
                'satuan': komponen.satuan, 'jabatan': komponen.jabatan.id
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatekomponenlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            komponen = result['komponen']
            besaran = result['besaran']
            satuan = result['satuan']
            jabatan = result['jabatan']
            print(result)
            komponenlembur = KomponenLembur(jenis_komponen=komponen, besaran=besaran,
                                            satuan=satuan, jabatan_id=jabatan)
            try:
                print('disini')
                komponenlembur.save()
                success = {
                    'komponen': komponenlembur.id, 'komponenlembur': komponenlembur.jenis_komponen,
                    'besaran': komponenlembur.besaran, 'satuan': komponenlembur.satuan,
                    'jabatan': komponenlembur.jabatan.jabatan
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditkomponenlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            komponen = result['komponen']
            besaran = result['besaran']
            satuan = result['satuan']
            jabatan = result['jabatan']
            editkomponen = KomponenLembur.objects.get(id=result['idkomponen'])
            editkomponen.jenis_komponen = komponen
            editkomponen.besaran = besaran
            editkomponen.satuan = satuan
            editkomponen.jabatan = Jabatan.objects.get(id=jabatan)
            try:
                editkomponen.save()
                success = {
                    'komponen': editkomponen.id, 'komponenlembur': editkomponen.jenis_komponen,
                    'besaran': editkomponen.besaran, 'satuan': editkomponen.satuan,
                    'jabatan': editkomponen.jabatan.jabatan
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletekomponenlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            komponen = result['idkomponen']
            delkomponen = KomponenLembur.objects.get(id=komponen)
            try:
                delkomponen.delete()
                success = {
                    'komponen': komponen
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            lembur = Lembur.objects.get(id=result['lembur'])
            success = {
                'lembur': lembur.id, 'deskripsi': lembur.deskripsi_pekerjaan, 'pegawai': lembur.pegawai.user.first_name + ' ' + lembur.pegawai.user.last_name,
                'pegawaiid': lembur.pegawai.id, 'status': lembur.status.id, 'jenis': lembur.jenis_lembur.id,
                'tempat': lembur.tempat, 'tanggal': lembur.tanggal, 'waktumulai': lembur.waktu_mulai, 'waktuselesai': lembur.waktu_selesai,
                'waktumasuk': lembur.waktu_masuk, 'waktukeluar': lembur.waktu_keluar, 'bantuan': lembur.bantuan,
                'makan': lembur.makan, 'transport': lembur.transport, 'lastmodified': lembur.last_modified,
                'lastmodifiedby': lembur.last_modified_by.user.first_name + ' ' + lembur.last_modified_by.user.last_name,
                'createdby': lembur.created_by.user.first_name + ' ' + lembur.created_by.user.last_name,
                'createdbyid': lembur.created_by.id
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatelembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            deskripsi = result['deskripsi']
            pegawai = result['pegawai']
            status = result['status']
            jenis = result['jenis']
            tempat = result['tempat']
            tanggal = result['tanggal']
            waktumulai = result['waktumulai']
            waktuselesai = result['waktuselesai']
            waktumasuk = None
            waktukeluar = None
            bantuan = None
            makan = None
            transport = None
            if result['waktumasuk'] != '':
                waktumasuk = result['waktumasuk']
            if result['waktukeluar'] != '':
                waktukeluar = result['waktukeluar']
            if result['bantuan'] != '':
                bantuan = result['bantuan']
            if result['makan'] != '':
                makan = result['makan']
            if result['transport'] != '':
                transport = result['transport']
            lastmodified = timezone.now()
            lastmodifiedby = Pegawai.objects.get(user_id=request.user.id)
            createdby = result['createdby']
            print(result)
            lembur = Lembur(deskripsi_pekerjaan=deskripsi, pegawai_id=pegawai, status_id=status, jenis_lembur_id=jenis,
                            tempat=tempat, tanggal=tanggal, waktu_mulai=waktumulai, waktu_selesai=waktuselesai,
                            waktu_masuk=waktumasuk, waktu_keluar=waktukeluar, bantuan=bantuan, makan=makan,
                            transport=transport, last_modified=lastmodified, last_modified_by_id=lastmodifiedby.id,
                            created_by_id=createdby)
            try:
                print('disini')
                lembur.save()
                success = {
                    'lembur': lembur.id, 'deskripsi': lembur.deskripsi_pekerjaan, 'pegawai': lembur.pegawai.user.first_name + ' ' + lembur.pegawai.user.last_name,
                    'status': lembur.status.status, 'jenis': lembur.jenis_lembur.jenis_lembur,
                    'tempat': lembur.tempat, 'tanggal': lembur.tanggal, 'waktumulai': lembur.waktu_mulai, 'waktuselesai': lembur.waktu_selesai,
                    'waktumasuk': lembur.waktu_masuk, 'waktukeluar': lembur.waktu_keluar, 'bantuan': lembur.bantuan,
                    'makan': lembur.makan, 'transport': lembur.transport, 'lastmodified': lembur.last_modified,
                    'lastmodifiedby': lembur.last_modified_by.user.first_name + ' ' + lembur.last_modified_by.user.last_name,
                    'createdby': lembur.created_by.user.first_name + ' ' + lembur.created_by.user.last_name
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            deskripsi = result['deskripsi']
            pegawai = result['pegawai']
            status = result['status']
            jenis = result['jenis']
            tempat = result['tempat']
            tanggal = result['tanggal']
            waktumulai = result['waktumulai']
            waktuselesai = result['waktuselesai']
            waktumasuk = None
            waktukeluar = None
            bantuan = None
            makan = None
            transport = None
            if result['waktumasuk'] != '':
                waktumasuk = result['waktumasuk']
            if result['waktukeluar'] != '':
                waktukeluar = result['waktukeluar']
            if result['bantuan'] != '':
                bantuan = result['bantuan']
            if result['makan'] != '':
                makan = result['makan']
            if result['transport'] != '':
                transport = result['transport']
            lastmodified = timezone.now()
            lastmodifiedby = Pegawai.objects.get(user_id=request.user.id)
            createdby = result['createdby']
            editlembur = Lembur.objects.get(id=result['idlembur'])
            editlembur.deskripsi = deskripsi
            editlembur.pegawai = Pegawai.objects.get(id=pegawai)
            editlembur.status = StatusLembur.objects.get(id=status)
            editlembur.jenis = JenisLembur.objects.get(id=jenis)
            editlembur.tempat = tempat
            editlembur.tanggal = tanggal
            editlembur.waktu_mulai = waktumulai
            print('depan')
            editlembur.waktu_selesai = waktuselesai
            print('belakang')
            editlembur.waktu_masuk = waktumasuk
            editlembur.waktu_keluar = waktukeluar
            editlembur.bantuan = bantuan
            editlembur.makan = makan
            editlembur.transport = transport
            editlembur.last_modified = lastmodified
            editlembur.last_modified_by = lastmodifiedby
            editlembur.created_by = Pegawai.objects.get(id=createdby)
            try:
                editlembur.save()
                success = {
                    'lembur': editlembur.id, 'deskripsi': editlembur.deskripsi_pekerjaan, 'pegawai': editlembur.pegawai.user.first_name + ' ' + editlembur.pegawai.user.last_name,
                    'status': editlembur.status.status, 'jenis': editlembur.jenis_lembur.jenis_lembur,
                    'tempat': editlembur.tempat, 'tanggal': editlembur.tanggal, 'waktumulai': editlembur.waktu_mulai, 'waktuselesai': editlembur.waktu_selesai,
                    'waktumasuk': editlembur.waktu_masuk, 'waktukeluar': editlembur.waktu_keluar, 'bantuan': editlembur.bantuan,
                    'makan': editlembur.makan, 'transport': editlembur.transport, 'lastmodified': editlembur.last_modified,
                    'lastmodifiedby': editlembur.last_modified_by.user.first_name + ' ' + editlembur.last_modified_by.user.last_name,
                    'createdby': editlembur.created_by.user.first_name + ' ' + editlembur.created_by.user.last_name
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletelembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            lembur = result['idlembur']
            dellembur = Lembur.objects.get(id=lembur)
            try:
                dellembur.delete()
                success = {
                    'lembur': lembur
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewstatuslembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            status = StatusLembur.objects.get(id=result['status'])
            success = {
                'status': status.id, 'statuslembur': status.status
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatestatuslembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            status = result['status']
            print(result)
            statuslembur = StatusLembur(status=status)
            try:
                print('disini')
                statuslembur.save()
                success = {
                    'status': statuslembur.id, 'statuslembur': statuslembur.status
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditstatuslembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            status = result['status']
            editstatus = StatusLembur.objects.get(id=result['idstatus'])
            editstatus.status = status
            try:
                editstatus.save()
                success = {
                    'status': editstatus.id, 'statuslembur': editstatus.status
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletestatuslembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            status = result['idstatus']
            delstatus = StatusLembur.objects.get(id=status)
            try:
                delstatus.delete()
                success = {
                    'status': status
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewunitkerja(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            unit = UnitKerja.objects.get(id=result['unit'])
            success = {
                'unit': unit.id, 'unitkerja': unit.unit
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreateunitkerja(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            unit = result['unit']
            print(result)
            unitkerja = UnitKerja(unit=unit)
            try:
                print('disini')
                unitkerja.save()
                success = {
                    'unit': unitkerja.id, 'unitkerja': unitkerja.unit
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditunitkerja(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            unit = result['unit']
            editunit = UnitKerja.objects.get(id=result['idunit'])
            editunit.unit = unit
            try:
                editunit.save()
                success = {
                    'unit': editunit.id, 'unitkerja': editunit.unit
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeleteunitkerja(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            unit = result['idunit']
            delunit = UnitKerja.objects.get(id=unit)
            try:
                delunit.delete()
                success = {
                    'unit': unit
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mdviewpermissionlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            permission = PermissionLembur.objects.get(id=result['permission'])
            success = {
                'permission': permission.id, 'permissionlembur': permission.permission
            }
            print(json.dumps(success, cls=DjangoJSONEncoder))
            return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdcreatepermissionlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            permission = result['permission']
            print(result)
            permissionlembur = PermissionLembur(permission=permission)
            try:
                print('disini')
                permissionlembur.save()
                success = {
                    'permission': permissionlembur.id, 'permissionlembur': permissionlembur.permission
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
        else:
            print("gagal")
    except Exception as e:
        print(e)

@login_required()
def mdeditpermissionlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            permission = result['permission']
            editpermission = PermissionLembur.objects.get(id=result['idpermission'])
            editpermission.permission = permission
            try:
                editpermission.save()
                success = {
                    'permission': editpermission.id, 'permissionlembur': editpermission.permission
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@login_required()
def mddeletepermissionlembur(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            result = request.POST
            permission = result['idpermission']
            delpermission = PermissionLembur.objects.get(id=permission)
            try:
                delpermission.delete()
                success = {
                    'permission': permission
                }
                print(json.dumps(success, cls=DjangoJSONEncoder))
                return HttpResponse(json.dumps(success, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)