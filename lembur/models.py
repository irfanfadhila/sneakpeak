from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Create your models here.

class UnitKerja(models.Model):
    unit = models.CharField(_('nama unit kerja'), max_length=50)

class Jabatan(models.Model):
    jabatan = models.CharField(_('nama jabatan'), max_length=100)

class PermissionLembur(models.Model):
    permission = models.CharField(_('nama permission'), max_length=100)

class Pegawai(models.Model):
    user = models.ForeignKey(User)
    nip = models.IntegerField(_('nip'))
    jabatan = models.ForeignKey(Jabatan)
    unit = models.ForeignKey(UnitKerja)
    telepon = models.CharField(_('telepon'), max_length=15, null=True)
    permission = models.ForeignKey(PermissionLembur, blank=True, null=True)

class StatusLembur(models.Model):
    status = models.CharField(_('nama status'), max_length=50)

class JenisLembur(models.Model):
    jenis_lembur = models.CharField(_('nama jenis lembur'), max_length=50)

class Lembur(models.Model):
    pegawai = models.ForeignKey(Pegawai)
    deskripsi_pekerjaan = models.TextField()
    tanggal = models.DateField()
    tempat = models.TextField()
    waktu_mulai = models.TimeField()
    waktu_selesai = models.TimeField()
    jenis_lembur = models.ForeignKey(JenisLembur)
    status = models.ForeignKey(StatusLembur)
    waktu_masuk = models.TimeField(blank=True, null=True)
    waktu_keluar = models.TimeField(blank=True, null=True)
    bantuan = models.IntegerField(blank=True, null=True)
    makan = models.IntegerField(blank=True, null=True)
    transport = models.IntegerField(blank=True, null=True)
    last_modified = models.DateTimeField()
    created_by = models.ForeignKey(Pegawai, related_name='created_by')
    last_modified_by = models.ForeignKey(Pegawai, related_name='last_modified_by')

class KomponenLembur(models.Model):
    jabatan = models.ForeignKey(Jabatan)
    jenis_komponen = models.CharField(_('komponen uang lembur'), max_length=50)
    besaran = models.CommaSeparatedIntegerField(_('besaran uang lembur'), max_length=20, blank=True)
    satuan = models.CharField(_('satuan lembur'), max_length=10, blank=True)