import csv
from django.core.management.base import BaseCommand
from booking_venue.models import Venue

class Command(BaseCommand):
    help = 'Load venues from CSV file'

    def handle(self, *args, **options):
        with open('Football Stadiums.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip if not UEFA or AFC (football venues)
                if row['Confederation'] not in ['UEFA', 'AFC']:
                    continue

                # Create venue with appropriate data
                venue, created = Venue.objects.get_or_create(
                    name=row['Stadium'],
                    defaults={
                        'location': f"{row['City']}, {row['Country']}",
                        'capacity': int(row['Capacity']) if row['Capacity'].isdigit() else 10000,
                        'description': f"Football stadium in {row['City']}, {row['Country']}. Home to: {row['HomeTeams']}",
                        'price': 100.00  # Default price
                    }
                )
                if created:
                    self.stdout.write(f'Created venue: {venue.name}')
                else:
                    self.stdout.write(f'Venue already exists: {venue.name}')