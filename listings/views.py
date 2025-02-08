import uuid
import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email, send_payment_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        # creates Booking object using validated data
        booking = serializer.save()

        recipient_email = 'test@example.com'
        message = f"""
        Thank you for your booking! 
        
        Booking ID: {booking.booking_id}
        Listing: {booking.listing.name}
        Start Date: {booking.start_date}
        End Date: {booking.end_date}
        Total Price: {booking.total_price}
        Status: {booking.status}
        """

        # trigger the email task asynchronously
        send_booking_confirmation_email.delay(recipient_email, message)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        # Send payment confirmation email asynchronously
        recipient_email = "testuser@example.com"
        send_payment_confirmation_email.delay(recipient_email) # payment.booking.user.email

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        try:
            booking = Booking.objects.get(booking_id=pk)
            # if hasattr(booking, 'payment'):
            if Payment.objects.filter(booking=booking, payment_status="pending").exists():
                return Response({'error': 'Payment already initiated for this booking'}, status=status.HTTP_400_BAD_REQUEST)
        
            transaction_id = f"CHAPA_{uuid.uuid4().hex}"

            # Prepare Chapa API request
            url = "https://api.chapa.co/v1/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "amount": str(booking.total_price),
                "currency": "ETB",
                "email": "test@gmail.com",  # booking.user.email,
                "first_name": "John",       # booking.user.first_name,
                "last_name": "Doe",         # booking.user.last_name,
                "tx_ref": transaction_id,
                "callback_url": settings.CHAPA_CALLBACK_URL,
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 'success':
                checkout_url = response_data["data"]["checkout_url"]
                
                # Save payment record
                payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                transaction_id=transaction_id,
                payment_status='pending',
            )
                return Response({"payment_url": checkout_url, "transaction_id": transaction_id})
            
            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST) 

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['get'])
    def verify_payment(self, request, pk=None):
        # Verify payment with Chapa API

        try:
            payment = Payment.objects.get(booking_id=pk)

            url = f"https://api.chapa.co/v1/transaction/verify/{payment.transaction_id}"
            headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

            response = requests.get(url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                payment.payment_status = "completed"
            else:
                payment.payment_status = "failed"

            payment.save()
            return Response({"status": payment.payment_status})
        
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
