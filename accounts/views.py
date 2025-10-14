import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import CustomUser
from .forms import RegisterForm


def login_page(request):
    return render(request, 'accounts/login.html')


def register_page(request):
    return render(request, 'accounts/register.html')


@require_POST
@csrf_exempt
def login_ajax(request):
    data = json.loads(request.body)
    user = authenticate(username=data['username'], password=data['password'])
    if user:
        login(request, user)
        return JsonResponse({'success': True, 'role': user.role})
    return JsonResponse({'success': False, 'message': 'Username atau password salah'})


@require_POST
@csrf_exempt
def register_ajax(request):
    data = json.loads(request.body)
    form = RegisterForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})


@login_required
def dashboard(request):
    if request.user.role == 'admin':
        users = CustomUser.objects.filter(role='user')
        return render(request, 'accounts/dashboard_admin.html', {'users': users})
    return render(request, 'accounts/dashboard_user.html')


@login_required
def admin_delete_user(request, user_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False})
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return JsonResponse({'success': True})


@login_required
def logout_ajax(request):
    logout(request)
    return JsonResponse({'success': True})
