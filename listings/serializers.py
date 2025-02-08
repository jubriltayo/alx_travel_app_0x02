from rest_framework import serializers
from listings.models import Listing, Booking, Payment


class ListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Listing
        fields = [
            'listing_id',
            'name',
            'description',
            'location',
            'price_per_night',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['listing_id','created_at', 'updated_at']



class BookingSerializer(serializers.ModelSerializer):

    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'listing',
            'start_date',
            'end_date',
            'total_price',
            'status',
            'created_at',
        ]
        read_only_fields = ['booking_id','created_at']

    def validate(self, data):
        """
        Custom validation method.
        Ensures that the start_date is earlier than the end_date.
        Raises:
            serializers.ValidationError: If start_date is not before end_date.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("Start date must be before end date.")
        return data


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'booking',
            'transaction_id',
            'amount',
            'payment_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['payment_id', 'transaction_id', 'payment_status', 'created_at', 'updated_at']