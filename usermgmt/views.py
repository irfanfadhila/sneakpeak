from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from .forms import UserForm, PermissionForm, GpermForm, UpermForm
from django.contrib.admin.models import LogEntry
from django.utils.encoding import force_unicode

# action_flag = {1: "insert", 2: "update", 3: "delete", 4: "view"}

# Create your views here.
@login_required()
def index(request):
    cursor = 'usrmgmt'
    user_list = User.objects.all()
    groups = Group.objects.all()
    forms = UserForm()
    permission = Permission.objects.all()
    formperm = PermissionForm()
    gperm = Group.permissions.through.objects.all()
    formgperm = GpermForm()
    uperm = User.user_permissions.through.objects.all()
    formuperm = UpermForm()

    LogEntry.objects.log_action(
        object_id=None,
        object_repr="user management",
        action_flag=4,
        change_message="membuka halaman user management",
        content_type_id=None,
        user_id=request.user.pk
    )

    return render(request, 'usermgmt/index.html', {
        'list_user':user_list,
        'groups':groups,
        'perm':permission,
        'gperm':gperm,
        'uperm':uperm,
        'forms':forms,
        'formperm':formperm,
        'formgperm':formgperm,
        'formuperm':formuperm,
        'cursor':cursor
    })

def createUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            role = form.cleaned_data['role']
            new_user = User(username=username, password=password, first_name=first_name, last_name=last_name)
            new_user.save()

            LogEntry.objects.log_action(
                object_id=new_user.id,
                object_repr=force_unicode(new_user),
                action_flag=1,
                change_message="membuat user baru",
                content_type_id=ContentType.objects.get_for_model(new_user).pk,
                user_id=request.user.pk
            )

            if role is not None:
                new_user.groups.add(role)
    return index(request)

def viewUser(request, id):
    cursor = 'usrmgmt'
    user = get_object_or_404(User, id=id)
    if user.groups.count() > 0:
        role = Group.objects.get(name=user.groups.all()[0])
        forms = UserForm({
            'username': user.username,
            'password': user.password,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
        })
    else:
        forms = UserForm({
            'username': user.username,
            'password': user.password,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

    LogEntry.objects.log_action(
        object_id=user.id,
        object_repr=force_unicode(user),
        action_flag=4,
        change_message="melihat user detail",
        content_type_id=ContentType.objects.get_for_model(user).pk,
        user_id=request.user.pk
    )

    return render(request, 'usermgmt/viewuser.html', {'user':user, 'forms': forms, 'cursor':cursor})

def editUser(request, id):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            role = form.cleaned_data['role']
            edit_user = User.objects.get(id=id)
            edit_user.username = username
            edit_user.password = password
            edit_user.first_name = first_name
            edit_user.last_name = last_name
            edit_user.save()

            LogEntry.objects.log_action(
                object_id=edit_user.id,
                object_repr=force_unicode(edit_user),
                action_flag=2,
                change_message="mengupdate data user",
                content_type_id=ContentType.objects.get_for_model(edit_user).pk,
                user_id=request.user.pk
            )

            if role is not None:
                if edit_user.groups.count() > 0:
                    user_group = User.groups.through.objects.get(user=edit_user)
                    user_group.group = role
                    user_group.save()
                else:
                    edit_user.groups.add(role)
    return viewUser(request, id)

def deleteUser(request, id):
    user = User.objects.get(id=id)
    user.delete()

    LogEntry.objects.log_action(
        object_id=user.id,
        object_repr=force_unicode(user),
        action_flag=3,
        change_message="menghapus data user",
        content_type_id=ContentType.objects.get_for_model(user).pk,
        user_id=request.user.pk
    )

    return index(request)

def createPermission(request):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            content_type = form.cleaned_data['content_type']
            codename = form.cleaned_data['codename']
            new_perm = Permission(name=name, content_type_id=content_type.id, codename=codename)
            new_perm.save()

            LogEntry.objects.log_action(
                object_id=new_perm.id,
                object_repr=force_unicode(new_perm),
                action_flag=1,
                change_message="membuat permission baru",
                content_type_id=ContentType.objects.get_for_model(new_perm).pk,
                user_id=request.user.pk
            )

    return index(request)

def viewPermission(request, id):
    cursor = 'usrmgmt'
    perm = get_object_or_404(Permission, id=id)
    ct = ContentType.objects.get(id=perm.content_type_id)
    forms = PermissionForm({
        'name': perm.name,
        'content_type': ct,
        'codename': perm.codename,
    })

    LogEntry.objects.log_action(
        object_id=perm.id,
        object_repr=force_unicode(perm),
        action_flag=4,
        change_message="melihat detail permission",
        content_type_id=ContentType.objects.get_for_model(perm).pk,
        user_id=request.user.pk
    )

    return render(request, 'usermgmt/viewpermission.html', {'perm':perm, 'forms': forms, 'cursor':cursor})

def editPermission(request, id):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            content_type = form.cleaned_data['content_type']
            codename = form.cleaned_data['codename']
            edit_perm = Permission.objects.get(id=id)
            edit_perm.name = name
            edit_perm.content_type_id = content_type.id
            edit_perm.codename = codename
            edit_perm.save()

            LogEntry.objects.log_action(
                object_id=edit_perm.id,
                object_repr=force_unicode(edit_perm),
                action_flag=2,
                change_message="mengupdate data permission",
                content_type_id=ContentType.objects.get_for_model(edit_perm).pk,
                user_id=request.user.pk
            )

    return viewPermission(request, id)

def createGroupPerm(request):
    if request.method == 'POST':
        form = GpermForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            perm = form.cleaned_data['perm']
            new_gperm = Group.objects.get(id=group.id)
            new_gperm.permissions.add(perm)

            LogEntry.objects.log_action(
                object_id=new_gperm.id,
                object_repr=force_unicode(new_gperm),
                action_flag=1,
                change_message="membuat group permission baru",
                content_type_id=ContentType.objects.get_for_model(new_gperm).pk,
                user_id=request.user.pk
            )

    return index(request)

def viewGroupPerm(request, id):
    cursor = 'usrmgmt'
    gperm = get_object_or_404(Group.permissions.through.objects, id=id)
    group = Group.objects.get(id=gperm.group.id)
    perm = Permission.objects.get(id=gperm.permission.id)
    forms = GpermForm({
        'group': group,
        'perm': perm,
    })

    LogEntry.objects.log_action(
        object_id=gperm.id,
        object_repr=force_unicode(gperm),
        action_flag=4,
        change_message="membuat data group permission",
        content_type_id=ContentType.objects.get_for_model(gperm).pk,
        user_id=request.user.pk
    )

    return render(request, 'usermgmt/viewgperm.html', {'gperm':gperm, 'forms': forms, 'cursor':cursor})

def editGroupPerm(request, id):
    if request.method == 'POST':
        form = GpermForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            perm = form.cleaned_data['perm']
            edit_gperm = Group.permissions.through.objects.get(id=id)
            edit_gperm.group_id = group.id
            edit_gperm.permission_id = perm.id
            edit_gperm.save()

            LogEntry.objects.log_action(
                object_id=edit_gperm.id,
                object_repr=force_unicode(edit_gperm),
                action_flag=2,
                change_message="mengupdate data group permission",
                content_type_id=ContentType.objects.get_for_model(new_user).pk,
                user_id=request.user.pk
            )

    return viewGroupPerm(request, id)

def createUserPerm(request):
    if request.method == 'POST':
        form = UpermForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            perm = form.cleaned_data['perm']
            new_uperm = User.objects.get(id=user.id)
            new_uperm.permissions.add(perm)

            LogEntry.objects.log_action(
                object_id=new_uperm.id,
                object_repr=force_unicode(new_uperm),
                action_flag=1,
                change_message="membuat user permission baru",
                content_type_id=ContentType.objects.get_for_model(new_uperm).pk,
                user_id=request.user.pk
            )

    return index(request)

def viewUserPerm(request, id):
    cursor = 'usrmgmt'
    uperm = get_object_or_404(User.user_permissions.through.objects, id=id)
    user = User.objects.get(id=uperm.user.id)
    perm = Permission.objects.get(id=uperm.permission.id)
    forms = UpermForm({
        'user': user,
        'perm': perm,
    })

    LogEntry.objects.log_action(
        object_id=uperm.id,
        object_repr=force_unicode(uperm),
        action_flag=4,
        change_message="melihat detail user permission",
        content_type_id=ContentType.objects.get_for_model(uperm).pk,
        user_id=request.user.pk
    )

    return render(request, 'usermgmt/viewuperm.html', {'uperm':uperm, 'forms': forms, 'cursor':cursor})

def editUserPerm(request, id):
    if request.method == 'POST':
        form = UpermForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            perm = form.cleaned_data['perm']
            edit_uperm = User.user_permissions.through.objects.get(id=id)
            edit_uperm.user_id = user.id
            edit_uperm.permission_id = perm.id
            edit_uperm.save()

            LogEntry.objects.log_action(
                object_id=edit_uperm.id,
                object_repr=force_unicode(edit_uperm),
                action_flag=2,
                change_message="mengupdate data user permission",
                content_type_id=ContentType.objects.get_for_model(edit_uperm).pk,
                user_id=request.user.pk
            )

    return viewUserPerm(request, id)
