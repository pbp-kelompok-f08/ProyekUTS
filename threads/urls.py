# threads/urls.py
from django.urls import path
from . import views

app_name = "threads"

urlpatterns = [
    path('', views.show_main, name='show_main'),
    path('json/', views.show_json, name='show_json'),
    path('create-thread-ajax/', views.add_thread_entry_ajax, name='add_thread_entry_ajax'),
]
