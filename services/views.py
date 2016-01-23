__author__ = 'irfan'

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
# import mysql.connector
import json
from django.http import HttpResponse

def index(request):
    return render(request, 'services/index.html')

def getDosen(request):
    user = User.objects.all()
    """
    conn = mysql.connector.connect(
        user='operasional',
        password='sidang2014',
        host='sidang.int.cs.ui.ac.id',
        database='sisidangdb_2015',
    )
    cursor = conn.cursor()

    query = (
        "SELECT nip, nama, email FROM mainapp_dosen"
    )

    cursor.execute(query)

    rows = cursor.fetchall()
    """

    rowarray_list = []
    for row in user:
        t = (row.username, row.first_name, row.email)
        rowarray_list.append(t)
    j = json.dumps(rowarray_list)
    rowarrays_file = 'student_rowarrays.js'
    f = open(rowarrays_file,'w')
    print >> f, j

    return HttpResponse(j, content_type="application/json")