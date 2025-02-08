from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(recipient_email, message):
    """
    Send a booking confirmation email asynchronously
    """
    subject = "Booking Confirmation"
    sender = settings.EMAIL_HOST_USER # OR "no-reply@alxtravel.com"

    recipient_list = [recipient_email]
    
    send_mail(subject, message, sender, recipient_list)

@shared_task
def send_payment_confirmation_email(recipient_email):
    """
    Send a booking confirmation email asynchronously
    """
    subject = "Payment Confirmation"
    message = f"Your booking has been received and confirmed"
    sender = settings.EMAIL_HOST_USER # OR "no-reply@alxtravel.com"

    recipient_list = [recipient_email]

    send_mail(subject, message, sender, recipient_list)