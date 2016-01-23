# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Jabatan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jabatan', models.CharField(max_length=100, verbose_name='nama jabatan')),
            ],
        ),
        migrations.CreateModel(
            name='JenisLembur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jenis_lembur', models.CharField(max_length=50, verbose_name='nama jenis lembur')),
            ],
        ),
        migrations.CreateModel(
            name='KomponenLembur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jenis_komponen', models.CharField(max_length=50, verbose_name='komponen uang lembur')),
                ('besaran', models.CommaSeparatedIntegerField(max_length=20, verbose_name='besaran uang lembur', blank=True)),
                ('satuan', models.CharField(max_length=10, verbose_name='satuan lembur', blank=True)),
                ('jabatan', models.ForeignKey(to='lembur.Jabatan')),
            ],
        ),
        migrations.CreateModel(
            name='Lembur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deskripsi_pekerjaan', models.TextField()),
                ('tanggal', models.DateField()),
                ('tempat', models.TextField()),
                ('waktu_mulai', models.TimeField()),
                ('waktu_selesai', models.TimeField()),
                ('waktu_masuk', models.TimeField(null=True, blank=True)),
                ('waktu_keluar', models.TimeField(null=True, blank=True)),
                ('bantuan', models.IntegerField(null=True, blank=True)),
                ('makan', models.IntegerField(null=True, blank=True)),
                ('transport', models.IntegerField(null=True, blank=True)),
                ('last_modified', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Pegawai',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nip', models.IntegerField(verbose_name='nip')),
                ('telepon', models.CharField(max_length=15, null=True, verbose_name='telepon')),
                ('jabatan', models.ForeignKey(to='lembur.Jabatan')),
            ],
        ),
        migrations.CreateModel(
            name='PermissionLembur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(max_length=100, verbose_name='nama permission')),
            ],
        ),
        migrations.CreateModel(
            name='StatusLembur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=50, verbose_name='nama status')),
            ],
        ),
        migrations.CreateModel(
            name='UnitKerja',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unit', models.CharField(max_length=50, verbose_name='nama unit kerja')),
            ],
        ),
        migrations.AddField(
            model_name='pegawai',
            name='permission',
            field=models.ForeignKey(blank=True, to='lembur.PermissionLembur', null=True),
        ),
        migrations.AddField(
            model_name='pegawai',
            name='unit',
            field=models.ForeignKey(to='lembur.UnitKerja'),
        ),
        migrations.AddField(
            model_name='pegawai',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lembur',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', to='lembur.Pegawai'),
        ),
        migrations.AddField(
            model_name='lembur',
            name='jenis_lembur',
            field=models.ForeignKey(to='lembur.JenisLembur'),
        ),
        migrations.AddField(
            model_name='lembur',
            name='last_modified_by',
            field=models.ForeignKey(related_name='last_modified_by', to='lembur.Pegawai'),
        ),
        migrations.AddField(
            model_name='lembur',
            name='pegawai',
            field=models.ForeignKey(to='lembur.Pegawai'),
        ),
        migrations.AddField(
            model_name='lembur',
            name='status',
            field=models.ForeignKey(to='lembur.StatusLembur'),
        ),
    ]
