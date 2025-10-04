from django.shortcuts import render


def home(request):
    """Render halaman beranda sederhana dengan tautan ke daftar match."""
    return render(request, "home.html")
