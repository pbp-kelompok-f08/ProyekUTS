from django.shortcuts import render
from django.contrib.auth.decorators import login_required



@login_required
def home(request):
    """Render halaman beranda sederhana dengan tautan ke daftar match."""
    return render(request, "home.html")
