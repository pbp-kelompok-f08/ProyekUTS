# threads/urls.py
from django.urls import path
from . import views

app_name = "threads"

urlpatterns = [
    path('', views.show_main, name='show_main'),
    path('json/', views.show_json, name='show_json'),
    path('create-thread-ajax/', views.add_thread_entry_ajax, name='add_thread_entry_ajax'),
    path('create-reply-ajax/<uuid:threadId>/', views.add_reply_entry_ajax, name='add_reply_entry_ajax'),
    path('replies/<str:threadId>/', views.get_replies_by_threadId, name='get_replies_by_threadId'),
]
