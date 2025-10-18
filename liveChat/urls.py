from django.urls import path
from .views import operate_chat_by_group, testing, operate_group

app_name = 'liveChat'

urlpatterns = [
    path('', testing, name='testing'),
    path('<uuid:group_id>/', operate_chat_by_group, name='operate_chat_by_group'),
    path('group/', operate_group, name='operate_group'),
    path('group/<uuid:group_id>/', operate_group, name='operate_group')
]

