from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Venue, Booking
from datetime import date, time


class VenueModelTest(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Test Stadium",
            location="Jakarta, Indonesia",
            capacity=50000,
            description="A beautiful football stadium",
            price=100.00
        )

    def test_venue_creation(self):
        """Test that a venue can be created with correct attributes"""
        self.assertEqual(self.venue.name, "Test Stadium")
        self.assertEqual(self.venue.location, "Jakarta, Indonesia")
        self.assertEqual(self.venue.capacity, 50000)
        self.assertEqual(str(self.venue), "Test Stadium")

    def test_venue_str_method(self):
        """Test the string representation of Venue model"""
        self.assertEqual(str(self.venue), "Test Stadium")


class BookingModelTest(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create a test venue
        self.venue = Venue.objects.create(
            name="Test Stadium",
            location="Jakarta, Indonesia",
            capacity=50000,
            description="A beautiful football stadium",
            price=100.00
        )

        # Create a test booking
        self.booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            date=date.today(),
            time=time(14, 0),  # 2:00 PM
            status='pending'
        )

    def test_booking_creation(self):
        """Test that a booking can be created with correct attributes"""
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.venue, self.venue)
        self.assertEqual(self.booking.status, 'pending')
        self.assertEqual(str(self.booking), f"{self.user.username} - {self.venue.name} on {self.booking.date}")

    def test_booking_status_choices(self):
        """Test that booking status choices are valid"""
        valid_statuses = ['pending', 'confirmed', 'cancelled']
        for status in valid_statuses:
            booking = Booking.objects.create(
                user=self.user,
                venue=self.venue,
                date=date.today(),
                time=time(15, 0),
                status=status
            )
            self.assertEqual(booking.status, status)

    def test_booking_str_method(self):
        """Test the string representation of Booking model"""
        expected_str = f"{self.user.username} - {self.venue.name} on {self.booking.date}"
        self.assertEqual(str(self.booking), expected_str)


class VenueViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.venue = Venue.objects.create(
            name="Test Stadium",
            location="Jakarta, Indonesia",
            capacity=50000,
            description="A beautiful football stadium",
            price=100.00
        )

    def test_main_page_view(self):
        """Test that main page loads successfully"""
        response = self.client.get(reverse('booking_venue:main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_page.html')
        self.assertContains(response, self.venue.name)

    def test_api_venues_view(self):
        """Test the API endpoint for venues"""
        response = self.client.get(reverse('booking_venue:api_venues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()
        self.assertIn('venues', data)
        self.assertEqual(len(data['venues']), 1)
        self.assertEqual(data['venues'][0]['name'], self.venue.name)


class BookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.venue = Venue.objects.create(
            name="Test Stadium",
            location="Jakarta, Indonesia",
            capacity=50000,
            description="A beautiful football stadium",
            price=100.00
        )

    def test_book_venue_requires_login(self):
        """Test that booking a venue requires user to be logged in"""
        response = self.client.get(reverse('booking_venue:book_venue', args=[self.venue.id]))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_book_venue_authenticated(self):
        """Test that authenticated user can access booking page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking_venue:book_venue', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_venue.html')
        self.assertContains(response, self.venue.name)

    def test_my_bookings_requires_login(self):
        """Test that my bookings page requires user to be logged in"""
        response = self.client.get(reverse('booking_venue:my_bookings'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_my_bookings_authenticated(self):
        """Test that authenticated user can access my bookings page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking_venue:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_bookings.html')

    def test_cancel_booking_requires_login(self):
        """Test that canceling a booking requires user to be logged in"""
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            date=date.today(),
            time=time(14, 0),
            status='pending'
        )
        response = self.client.post(reverse('booking_venue:cancel_booking', args=[booking.id]))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_cancel_booking_authenticated(self):
        """Test that authenticated user can cancel their booking"""
        self.client.login(username='testuser', password='testpass123')
        booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            date=date.today(),
            time=time(14, 0),
            status='pending'
        )

        response = self.client.post(reverse('booking_venue:cancel_booking', args=[booking.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful cancellation

        # Check that booking was deleted
        booking_exists = Booking.objects.filter(id=booking.id).exists()
        self.assertFalse(booking_exists)


class BookingIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.venue = Venue.objects.create(
            name="Test Stadium",
            location="Jakarta, Indonesia",
            capacity=50000,
            description="A beautiful football stadium",
            price=100.00
        )

    def test_complete_booking_flow(self):
        """Test the complete booking flow from login to booking creation"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Access booking page
        response = self.client.get(reverse('booking_venue:book_venue', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)

        # Create a booking
        booking_data = {
            'date': date.today().isoformat(),
            'time': '15:00',
            'duration': '2'
        }

        response = self.client.post(
            reverse('booking_venue:book_venue', args=[self.venue.id]),
            booking_data
        )

        # Check that booking was created
        booking_exists = Booking.objects.filter(
            user=self.user,
            venue=self.venue,
            date=date.today(),
            time=time(15, 0)
        ).exists()
        self.assertTrue(booking_exists)

        # Check my bookings page shows the booking
        response = self.client.get(reverse('booking_venue:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.venue.name)
