# threads/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Thread, Reply
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



# @login_required
def show_main(request):
    return render(request,"main.html")

def show_json(request):
    thread_list = Thread.objects.all()
    data = [
        {
            # 'id': str(thread.id),
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

# def thread_list(request):
#     threads = Thread.objects.all().order_by('-created_at')
#     return render(request, 'threads/thread_list.html', {'threads': threads})

# def thread_detail(request, thread_id):
#     thread = get_object_or_404(Thread, id=thread_id)
#     replies = thread.replies.all()  # because of related_name="replies"
#     return render(request, 'threads/thread_detail.html', {'thread': thread, 'replies': replies})

# @login_required
# def create_thread(request):
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         image = request.POST.get('image', '')
#         thread = Thread.objects.create(user=request.user, content=content, image=image)
#         return redirect('thread_detail', thread_id=thread.id)
#     return render(request, 'threads/create_thread.html')

# @login_required
# def create_reply(request, thread_id):
#     thread = get_object_or_404(Thread, id=thread_id)
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         image = request.POST.get('image', '')
#         Reply.objects.create(user=request.user, thread=thread, content=content, image=image)
#         thread.changeReply(True)
#         return redirect('thread_detail', thread_id=thread.id)
#     return HttpResponse("Invalid request", status=400)

# @login_required
# def like_thread(request, thread_id):
#     thread = get_object_or_404(Thread, id=thread_id)
#     thread.changeLike(True)
#     return redirect('thread_detail', thread_id=thread.id)
