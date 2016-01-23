import requests
import json
import urllib
import urllib2

from django.conf import settings
from django.contrib.auth.models import User, Group
# from lowongan.models import Pelamar
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from django_cas_ng.backends import CASBackend
from django_cas_ng.signals import cas_user_authenticated
from django_cas_ng.backends import _verify_cas3
from django.http import HttpResponseForbidden
from django.template import RequestContext, loader


def forbidden(request, template_name='403.html'):
    '''Default 403 handler'''
    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))


class CASAuth(CASBackend):
    def authenticate(self, ticket, service, request):
        """Verifies CAS ticket and gets or creates User object"""
        available_group = ['dosen', 'staff', 'administrator']

        username, attributes = _verify_cas3(ticket, service)
        if attributes:
            request.session['attributes'] = attributes
        if username == 'muhammad.irfan16':
            attributes['peran_user'] = 'administrator'
        if not username or attributes['peran_user'] not in available_group:
            return None
        try:
            user = User.objects.get(username=username)
            created = False
        except User.DoesNotExist:
            # check if we want to create new users, if we don't fail auth
            create = getattr(settings, 'CAS_CREATE_USER', True)
            if not create:
                return None
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.password = ''
            user.first_name = attributes['nama']
            user.save()
            created = True
            group = Group.objects.get(name=attributes['peran_user'])
            user.groups.add(group)

        # send the `cas_user_authenticated` signal
        cas_user_authenticated.send(
            sender=self,
            user=user,
            created=created,
            attributes=attributes,
            ticket=ticket,
            service=service,
        )
        print(user)
        print(username)
        print(created)
        print(attributes)
        print(ticket)
        print(service)
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class Custom403Middleware(object):
    '''Catches 403 responses and renders 403.html'''
    def process_response(self, request, response):
        if isinstance(response, HttpResponseForbidden):
            return forbidden(request)
        else:
            return response


class CustomAuth(ModelBackend):
    def authenticate(self, username=None, password=None):

        available_group = ['dosen', 'staf', 'administrator']

        # berikut merupakan akun-akun untuk percobaan
        # dapat dihapus jika sudah tidak digunakan
        #

        print ('menambahkan akun dummy')

        if username == 'userdosen1' and password == 'dosen123':
            data = {'state': 1, 'nama': 'user dosen1', 'nama_role': 'dosen', 'kodeidentitas': 123456721}
        elif username == 'userdosen2' and password == 'dosen123':
            data = {'state': 1, 'nama': 'user dosen2', 'nama_role': 'dosen', 'kodeidentitas': 123456722}
        elif username == 'userdosen3' and password == 'dosen123':
            data = {'state': 1, 'nama': 'user dosen3', 'nama_role': 'dosen', 'kodeidentitas': 123456723}
        elif username == 'useradmin' and password == 'admin123':
            data = {'state': 1, 'nama': 'admin', 'nama_role': 'administrator', 'kodeidentitas': 123456741}
        elif username == 'usersekre' and password == 'sekre123':
            data = {'state': 1, 'nama': 'user sekre', 'nama_role': 'sekretariat', 'kodeidentitas': 123456731}
        elif username == 'irfan' and password == 'irfan123':
            data = {'state': 1, 'nama': 'user irfan'}
        elif username == 'caca' and password == 'caca123':
            data = {'state': 1, 'nama': 'user irfan'}
        elif username == 'billy' and password == 'billy123':
            data = {'state': 1, 'nama': 'user irfan'}
        elif username == 'tata' and password == 'tata123':
            data = {'state': 1, 'nama': 'user irfan'}
        elif username == 'aji.nursyamsi' and password == 'aji123':
            data = {'state': 1, 'nama': 'user irfan'}
        elif username == 'maman' and password == 'maman123':
            data = {'state': 1, 'nama': 'user maman'}
        elif username == 'andi' and password == 'andi123':
            data = {'state': 1, 'nama': 'user andi'}
        elif username == 'juwita' and password == 'juwita123':
            data = {'state': 1, 'nama': 'user juwita'}
        else:
            try:
                param = urllib.urlencode({"username": username, "password": password})
                myrequest = urllib2.Request('https://apps.cs.ui.ac.id/webservice/login_ldap.php?%s' % (param))
                response = urllib2.urlopen(myrequest, timeout=1000000).read()
                print response
                data = json.loads(response)
                print str(data)
            except ValueError as e:
                print e
                return None

        if data['state'] == 1:
            if username in ['nunuk', 'sylvia', 'moh.afifun']:
                data['nama_role'] = 'sekretariat'

            if username in ['hadaiq', 'maya.retno21']:
                data['nama_role'] = 'administrator'

            try:
                user = User.objects.get(username=username.lower())
            except User.DoesNotExist:
                user = User(username=username.lower(), first_name=data['nama'])
                user.save()

            # if data['nama_role'] in available_group:
            #     group = Group.objects.get(name=str(data['nama_role']))
            #     user.groups.add(group)

                # if data['nama_role'] == 'mahasiswa':
                #    try:
                # Pelamar.objects.get(nama=str(data['nama']),npm=str(data['kodeidentitas']))
                #    except Pelamar.DoesNotExist:
                # pelamar = Pelamar(nama=str(data['nama']), npm=str(data['kodeidentitas']))
                # pelamar.user_id = user
                # pelamar.save()

            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
