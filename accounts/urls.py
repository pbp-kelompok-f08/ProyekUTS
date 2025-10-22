from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('dashboard/', dashboard, name='dashboard'),

    path('ajax/login/', login_ajax, name='login_ajax'),
    path('ajax/register/', register_ajax, name='register_ajax'),
    path('ajax/logout/', logout_ajax, name='logout_ajax'),
    path('ajax/delete-user/<int:user_id>/', admin_delete_user, name='admin_delete_user'),
    path('ajax/users/', ajax_all_users, name='ajax_all_users'),
    path('ajax/profile/', profile, name='profile'),
]
