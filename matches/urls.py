from django.urls import path

from . import views

app_name = "matches"

urlpatterns = [
    path("", views.match_dashboard, name="dashboard"),
    path("create/", views.create_match, name="create_match"),
    path("<int:pk>/book/", views.book_match, name="book_match"),
]
