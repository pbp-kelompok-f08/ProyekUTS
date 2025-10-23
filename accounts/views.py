import json
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django.core import serializers
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
    return JsonResponse({'success': False, 'message': 'Username atau password salah'}, status=400)

@require_POST
@csrf_exempt
def register_ajax(request: HttpRequest):
    data = json.loads(request.body)
    form = RegisterForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def dashboard(request: HttpRequest):
    print(f"username: {request.user.username}, role: {request.user.role}")
    if request.user.role == 'admin':
        users = CustomUser.objects.all()
        return render(request, 'accounts/dashboard_admin.html', {'users': users})
    return render(request, 'accounts/dashboard_user.html')

@login_required
def ajax_all_users(request: HttpRequest):
    if request.user.role != 'admin':
        return HttpResponse(status=401)
    users = serializers.serialize("json", CustomUser.objects.filter(role='user'))
    admins = serializers.serialize("json", CustomUser.objects.filter(role='admin'))
    return JsonResponse({
        "users": json.loads(users),
        "admins": json.loads(admins)
    }, status=200)

@require_GET
def profile(request: HttpRequest):
    user = request.user
    if not user:
        return HttpRequest(status=401)
    data = model_to_dict(user)
    data["participation"] = user.participation
    print(data)
    return JsonResponse({"data": data}, status=200)

@login_required
def admin_delete_user(request, user_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False}, status=401)
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return JsonResponse({'success': True})

@login_required
def logout_ajax(request):
    logout(request)
    return JsonResponse({'success': True})
