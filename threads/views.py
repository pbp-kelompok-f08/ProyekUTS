# threads/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse

from accounts.models import CustomUser
from .models import Thread,ReplyChild

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



@login_required
def show_main(request):
    return render(request,"main.html")

def show_json(request):
    thread_list = Thread.objects.all().order_by('-created_at')
    data = [
        {
            'username': getattr(thread.user, 'username', 'Anonymous'),
            'id': str(thread.id),
            'content' :thread.content,
            'tags' : thread.tags,
            'image' : thread.image,
            'likeCount' : thread.likeCount,
            'shareCount' : thread.shareCount,
            'replyCount' : thread.replyCount,
            'created_at' : thread.created_at,
            "isLiked": request.user in thread.liked_by.all()
        }
        for thread in thread_list
    ]
    return JsonResponse(data, safe=False)

@login_required
@csrf_exempt
@require_POST
def add_thread_entry_ajax(request):
    user = request.user
    content = request.POST.get("content")
    tags = request.POST.get("tags")
    image = request.POST.get("image")

    new_thread = Thread(
        user=user,
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
            'username': getattr(reply.user, 'username', 'Anonymous'),
            'id': str(reply.id),
            'thread_id': str(reply.thread.id),
            'content': reply.content,
            'created_at': reply.created_at.isoformat(),
            'likeCount': reply.likeCount,
            "isLiked": request.user in reply.liked_by.all()

        }
        for reply in replies
    ]

    # return as JSON
    return JsonResponse(data, safe=False)

@login_required
@csrf_exempt
@require_POST
def add_reply_entry_ajax(request, threadId):
    content = request.POST.get("content", "").strip()
    parent_thread = Thread.objects.get(pk=threadId)
    parent_thread.changeReply(True)

    reply = ReplyChild.objects.create(
        thread=parent_thread,
        content=content,
        user = request.user
    )

    data = {
        "id": reply.id,
        "thread_id": reply.thread.id,
        "content": reply.content,
        "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "likeCount": reply.likeCount,
        "count":parent_thread.replyCount,
        'username': getattr(reply.user, 'username', 'Anonymous'),
    }

    return JsonResponse(data, status=201)

@login_required
@csrf_exempt
@require_POST
def like_thread_ajax(request, thread_id):

    try:
        thread = Thread.objects.get(pk=thread_id)
        user = request.user
        isLiked = thread.changeLike(user)
        data = {
            "likeCount":thread.likeCount,
            "isLiked": isLiked
        }
        return JsonResponse(data)

    except Thread.DoesNotExist:
        return JsonResponse({"success": False, "error": "Thread not found"}, status=404)
    
@login_required
@csrf_exempt
@require_POST
def like_reply_ajax(request, replyId):

    try:
        reply = ReplyChild.objects.get(pk=replyId)
        user = request.user
        isLiked = reply.changeLike(user)
        data = {
            "likeCount":reply.likeCount,
            "isLiked": isLiked
        }
        return JsonResponse(data)

    except Thread.DoesNotExist:
        return JsonResponse({"success": False, "error": "Thread not found"}, status=404)

