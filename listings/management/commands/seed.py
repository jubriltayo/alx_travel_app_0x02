from django.core.management.base import BaseCommand
from listings.models import Listing
import uuid
from random import randint
from faker import Faker


class Command(BaseCommand):
    """
    Custom Django management command to populate the database with sample listings data.
    """

    help = "Seeds the database sample listings data"

    def add_arguments(self, parser):
        """
        Number of listings to create
        """
        parser.add_argument('num_listings', type=int, help="Number of listings to create")


    def handle(self, *args, **kwargs):
        """
        The logic for creating the sample data and saving it to the database.
        This method runs when the `python manage.py seed` command is executed.
        """

        fake = Faker()

        # Number of listings to create
        num_listings = kwargs['num_listings']

        for _ in range(num_listings):
            # creating random sample data
            listing_id=str(uuid.uuid4())
            name = f"{fake.first_name().capitalize()}'s {fake.random_element(elements=["Villa", "Cottage", "Retreat", "Haven", "Lodge"])}"
            description = fake.text(max_nb_chars=200)
            location = fake.city()
            price_per_night = float(f"{randint(50, 1000)}.00")

            # create the listing instance and save in the database
            listing = Listing.objects.create(
                listing_id=listing_id,
                name=name,
                description=description,
                location=location,
                price_per_night=price_per_night
            )

            self.stdout.write(self.style.SUCCESS(f"Successfully created listing: {listing.name}"))