import json
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Listing, Booking
from django.utils.timezone import now, timedelta


class ListingTests(APITestCase):
    def setUp(self):
        self.listing = Listing.objects.create(
            name="Sample Listing",
            description="A cozy place to stay.",
            location="Nigeria",
            price_per_night=100.00,
        )
        self.listing_url = "/api/listings/"

    def test_list_listings(self):
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_listing(self):
        data = {
            "name": "Test Listing",
            "description": "A test description",
            "location": "Cape Town",
            "price_per_night": 150.00,
        }
        response = self.client.post(
            self.listing_url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Listing.objects.count(), 2)

    def test_retrieve_listing(self):
        response = self.client.get(f"{self.listing_url}{self.listing.listing_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_listing(self):
        data = {
            "name": "Updated Listing",
            "description": self.listing.description,
            "location": self.listing.location,
            "price_per_night": str(self.listing.price_per_night),
        }
        response = self.client.put(
            f"{self.listing_url}{self.listing.listing_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.name, "Updated Listing")

    def test_delete_listing(self):
        response = self.client.delete(f"{self.listing_url}{self.listing.listing_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Listing.objects.count(), 0)


class BookingTests(APITestCase):
    def setUp(self):
        self.listing = Listing.objects.create(
            name="Sample Listing",
            description="A cozy place to stay.",
            location="Nigeria",
            price_per_night=100.00,
        )
        self.booking = Booking.objects.create(
            listing=self.listing,
            start_date=now().date(),
            end_date=(now() + timedelta(days=3)).date(),
            total_price=300.00,
        )
        self.booking_url = "/api/bookings/"

    def test_list_bookings(self):
        response = self.client.get(self.booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_booking(self):
        data = {
            "listing": str(self.listing.listing_id),
            "start_date": now().date().isoformat(),
            "end_date": (now() + timedelta(days=2)).date().isoformat(),
            "total_price": 200.00,
        }
        response = self.client.post(
            self.booking_url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)

    def test_retrieve_booking(self):
        response = self.client.get(f"{self.booking_url}{self.booking.booking_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_booking(self):
        data = {
            "listing": str(self.booking.listing.listing_id),
            "start_date": self.booking.start_date.isoformat(),
            "end_date": self.booking.end_date.isoformat(),
            "total_price": str(self.booking.total_price),
            "status": "confirmed",
        }
        response = self.client.put(
            f"{self.booking_url}{self.booking.booking_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "confirmed")


    def test_delete_booking(self):
        response = self.client.delete(f"{self.booking_url}{self.booking.booking_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.count(), 0)
