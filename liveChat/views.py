from django.shortcuts import render, get_object_or_404
from .models import Group, Chat
from django.core import serializers
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
import uuid
import json

# Create your views here.
def testing(request: HttpRequest):
    return JsonResponse({
        "message": "hello"
    }, status=200)

@login_required
def operate_group(request: HttpRequest, group_id: uuid = ''):
    if request.method == "GET":
        return operate_group_get(request.user, group_id)
    elif request.method == "POST":
        return operate_group_post(request)
    elif request.method == "PATCH":
        return operate_group_patch(request, group_id)
    return HttpResponse(status=405)

def operate_group_get(user: CustomUser, group_id: uuid):
    if group_id:
        group = get_object_or_404(Group, id=group_id)
    elif user.role != 'admin':
        return HttpResponse(status=401)
    else:
        group = Group.objects.all()
    data = serializers.serialize("json", group)
    return JsonResponse({
        "data": data
    }, status=200)

def operate_group_post(request: HttpRequest):
    body = json.loads(request.body)
    if (len(body["users"]) < 2):
        return JsonResponse({
            "message": "Minimum 2 users to create a group chat."
        }, status=400)
    group = Group(name=body["name"], users=body["users"])
    group.save()
    return HttpResponse("CREATED", status=201)

def operate_group_patch(request: HttpRequest, group_id: uuid):
    body = json.loads(request.body)
    group = get_object_or_404(Group, id=group_id)
    if (body['name']):
        group.name = body['name']
    if (body['user']):
        user = get_object_or_404(CustomUser, username=body['user'])
        group.users.add(user)
    return HttpResponse(status=204)

@login_required
def operate_chat_by_group(request: HttpRequest, group_id: uuid):
    if request.method == "GET":
        chats = Chat.objects.filter(group_id=group_id)
        data = serializers.serialize("json", chats)
        return JsonResponse(data=data, status=200)
    
    elif request.method == "POST":
        body = json.loads(request.body)
        chat = Chat(message=body["message"], group_id=group_id)
        chat.save()
        return HttpResponse(status=201)
    
    return HttpResponse(status=405)