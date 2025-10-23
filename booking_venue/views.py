from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Venue, Booking
from .forms import BookingForm


def main_page(request):
    """
    Halaman utama menampilkan daftar venue (stadion) yang bisa dipesan.
    """
    venues = Venue.objects.all()
    return render(request, 'main_page.html', {'venues': venues})


@login_required
def book_venue(request, venue_id):
    """
    View untuk melakukan booking stadion tertentu.
    - Menolak booking jika waktu sudah terpakai.
    - Menyimpan booking baru jika valid.
    """
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # Create booking manually
            booking = Booking(
                user=request.user,
                venue=venue,
                date=date,
                time=time,
                status='pending'
            )

            try:
                booking.save()
                messages.success(request, f'Booking stadion {venue.name} berhasil!')
                return redirect('booking_success')
            except Exception as e:
                messages.error(request, f'Error saving booking: {e}')
                return render(request, 'book_venue.html', {'form': form, 'venue': venue})
    else:
        form = BookingForm()

    return render(request, 'book_venue.html', {'form': form, 'venue': venue})


@login_required
def booking_success(request):
    """
    Halaman konfirmasi setelah booking berhasil.
    """
    return render(request, 'booking_success.html')


@login_required
def my_bookings(request):
    """
    Menampilkan daftar booking milik user yang sedang login.
    """
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    """
    Menghapus booking jika milik user tersebut.
    """
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        messages.success(request, 'Booking telah dibatalkan.')
    return redirect('booking_venue:my_bookings')


def register(request):
    """
    View untuk registrasi user baru.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

