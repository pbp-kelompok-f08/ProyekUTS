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

@login_required
def profile_page(request):
    return render(request, "accounts/profile.html")

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

@require_GET
@login_required
def profile_detail(request: HttpRequest):
    user = request.user
    data = model_to_dict(user, fields=[
        'username', 'email', 'bio', 'role',
        'favorite_sport', 'skill_level'
    ])
    data["profile_picture"] = user.profile_picture.url if user.profile_picture else None
    return JsonResponse({"data": data}, status=200)

@login_required
@require_POST
def update_profile(request):
    user = request.user

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    bio = request.POST.get("bio", "").strip()
    favorite_sport = request.POST.get("favorite_sport", "").strip()
    skill_level = request.POST.get("skill_level", "").strip()
    profile_picture = request.FILES.get("profile_picture")
    remove_picture = request.POST.get("remove_picture")

    # --- Basic validation ---
    if not username:
        return JsonResponse({"status": "error", "message": "Username cannot be empty."}, status=400)

    # --- Update user fields ---
    user.username = username
    if email:
        user.email = email
    user.bio = bio
    user.favorite_sport = favorite_sport or None
    user.skill_level = skill_level or None
    if profile_picture:
        if user.profile_picture and user.profile_picture.name != profile_picture.name:
            user.profile_picture.delete(save=False)
        user.profile_picture = profile_picture

    if remove_picture == "true": 
        if user.profile_picture:
            user.profile_picture.delete(save=False)
        user.profile_picture = None
    elif profile_picture:
        if user.profile_picture and user.profile_picture.name != profile_picture.name:
            user.profile_picture.delete(save=False)
        user.profile_picture = profile_picture

    user.save()

    login(request, user)

    # --- Return updated data ---
    return JsonResponse({
        "status": "success",
        "data": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "favorite_sport": user.favorite_sport,
            "skill_level": user.skill_level,
            "profile_picture": user.profile_picture.url if user.profile_picture else None,
        }
    })