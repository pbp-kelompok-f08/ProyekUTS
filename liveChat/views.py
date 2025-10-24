from django.shortcuts import render, get_object_or_404
from .models import Group, Chat
from django.core import serializers
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from accounts.models import CustomUser
from .forms import *
import uuid
import json

# Create your views here.
@login_required
def show_main(request: HttpRequest):
    print("fetched group get")
    return render(request, 'main_livechat.html', {
        "username": request.user.username,
        "profile_picture": request.user.profile_picture.url if request.user.profile_picture else "https://cdn-icons-png.flaticon.com/512/847/847969.png",
    })

@login_required
@csrf_exempt
def operate_group(request: HttpRequest, group_id: uuid = ''):
    print("fetch here!")
    match request.method:
        case "GET":
            return operate_group_get(request, group_id)
        case "PATCH":
            return operate_group_patch(request, group_id)
        case "DELETE":
            return operate_group_delete(request.user, group_id)
        case _:
            return HttpResponse(status=405)

def operate_group_get(request: HttpRequest, group_id: uuid):
    user = request.user
    search_name = request.GET.get("group_name", "").lower()
    if user.role != 'admin' and group_id:
        group = get_object_or_404(Group, id=group_id)
        data = model_to_dict(group)
        data["members"] = group.users
        return JsonResponse({"data": data}, status=200)
    elif user.role != 'admin' and search_name:
        user_participations = user.participations.all()
        data = []
        for user_participation in user_participations:
            match = user_participation.match
            group = match.group
            if group.name.lower().count(search_name):
                group_dict = model_to_dict(group)
                group_dict["members"] = group.users
                group_dict["last_chat"] = group.last_chat
                print(group_dict)
                data.append(group_dict)
        return JsonResponse({"data": data}, status=200)
    elif user.role != 'admin':
        user_participations = user.participations.all()
        data = []
        for user_participation in user_participations:
            match = user_participation.match
            group = match.group
            group_dict = model_to_dict(group)
            group_dict["members"] = group.users
            group_dict["last_chat"] = group.last_chat
            print(group_dict)
            data.append(group_dict)
        return JsonResponse({"data": data}, status=200)
    elif group_id:
        group = get_object_or_404(Group, id=group_id)
        data = model_to_dict(group)
        data["members"] = group.users
        return JsonResponse({"data": data}, status=200)
    else:
        group = Group.objects.all()
        data = serializers.serialize("json", group)
        return JsonResponse({"data": json.loads(data)}, status=200)

def operate_group_patch(request: HttpRequest, group_id: uuid):
    data = json.loads(request.body)
    group = get_object_or_404(Group, id=group_id)
    if (data['name']):
        group.name = data['name']
    group.save()
    return HttpResponse(status=204)

def operate_group_delete(user: CustomUser, group_id: uuid = ''):
    if (user.role != 'admin'):
        return HttpResponse(status=401)
    elif (group_id):
        Group.objects.get(id=group_id).delete()
    else:
        Group.objects.all().delete()
    return HttpResponse(status=204)

@login_required
@csrf_exempt
def operate_chat_by_group(request: HttpRequest, group_id: uuid):
    print("here 2")
    match request.method:
        case "GET":
            return operate_chat_by_group_get(request.user, group_id)
        case "POST":
            return operate_chat_by_group_post(request, group_id)
        case "DELETE":
            return operate_chat_by_group_delete(request.user, group_id)
        case _: 
            return HttpResponse(status=405)

def operate_chat_by_group_get(user: CustomUser, group_id: uuid):
    group = get_object_or_404(Group, id=group_id)
    if user.role != 'admin' and not group.users.count(user.pk): 
        return HttpResponse(status=401)
    chats = list(group.chat.all().values("username", "message", "createdAt"))
    for chat in chats:
        user = CustomUser.objects.get(username=chat["username"])
        chat["profile_picture"] = user.profile_picture.url if user.profile_picture else "https://cdn-icons-png.flaticon.com/512/847/847969.png"
    return JsonResponse({"data": chats}, status=200)

def operate_chat_by_group_post(request: HttpRequest, group_id: uuid):
    data = json.loads(request.body)
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    if user.role != 'admin' and not group.users.count(user.pk): 
        return HttpResponse(status=401)
    chat = ChatForm({
        "group_id": group_id,
        "username": user.username,
        "message": data["message"],
        })
    if chat.is_valid():
        chat.save()
        return HttpResponse(status=201)
    return JsonResponse({"errors": chat.errors}, status=400)

def operate_chat_by_group_delete(user: CustomUser, group_id: uuid):
    if user.role == 'admin':
        Chat.objects.filter(group_id=group_id).delete()
        return HttpResponse(status=204)
    return HttpResponse(status=401)