# threads/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse

from accounts.models import CustomUser
from .models import Thread,ReplyChild

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



# @login_required
def show_main(request):
    return render(request,"main.html")

def show_json(request):
    thread_list = Thread.objects.all()
    data = [
        {
            'id': str(thread.id),
            'content' :thread.content,
            'tags' : thread.tags,
            'image' : thread.image,
            'likeCount' : thread.likeCount,
            'shareCount' : thread.shareCount,
            'replyCount' : thread.replyCount,
            'created_at' : thread.created_at,
        }
        for thread in thread_list
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def add_thread_entry_ajax(request):
    # user = request.user
    content = request.POST.get("content")
    tags = request.POST.get("tags")
    image = request.POST.get("image")

    new_thread = Thread(
        # user=user,
        content = content,
        tags =  tags,
        image = image,
    )
    new_thread.save()
    return HttpResponse(b"CREATED", status=201)


def get_replies_by_threadId(request, threadId):
    # get user or return 404

    # get all replies made by this user
    replies = ReplyChild.objects.filter(thread=threadId).order_by('-likeCount')

    # serialize the data manually (or you can use serializers)
    data = [
        {
            'id': str(reply.id),
            'thread_id': str(reply.thread.id),
            'content': reply.content,
            'created_at': reply.created_at.isoformat(),
            'likeCount': reply.likeCount,
        }
        for reply in replies
    ]

    # return as JSON
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def add_reply_entry_ajax(request, threadId):
    content = request.POST.get("content", "").strip()
    parent_thread = Thread.objects.get(pk=threadId)

    reply = ReplyChild.objects.create(
        thread=parent_thread,
        content=content,
        # user = request.user if you want to attach logged-in user
    )

    data = {
        "id": reply.id,
        "thread_id": reply.thread.id,
        "content": reply.content,
        "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "likeCount": reply.likeCount,
        # "user": reply.user.username if reply.user else "Anonymous"
    }

    return JsonResponse(data, status=201)

# @csrf_exempt
# @require_POST
# def add_reply_entry_ajax(request, threadId):
#     content = request.POST.get("content", "").strip()
#     parent_thread = Thread.objects.get(pk=threadId)

#     reply = ReplyChild.objects.create(
#         thread=parent_thread,
#         content=content,
#         # user = request.user if you want to attach logged-in user
#     )

#     reply.save()
#     return HttpResponse(b"CREATED", status=201)