# from django.core.management.base import BaseCommand
# from generate_report import main  # Import the main function from your original script

# class Command(BaseCommand):
#     help = 'Generates Bhavi Fashion reports based on various data models'

#     def add_arguments(self, parser):
#         parser.add_argument('--days', type=int, help='Filter reports to last N days', default=None)

#     def handle(self, *args, **options):
#         try:
#             main()  # Call the original main function with parsed arguments
#             self.stdout.write(self.style.SUCCESS('Reports generated successfully!'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'Error generating reports: {e}'))
from django.core.management.base import BaseCommand
from generate_report import main  # आपकी मुख्य रिपोर्ट जनरेशन स्क्रिप्ट

class Command(BaseCommand):
    help = 'Generates all reports for Bhavi Fashion'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            help='Filter reports by last N days'
        )

    def handle(self, *args, **options):
        try:
            main(days=options['days'])
            self.stdout.write(self.style.SUCCESS('Successfully generated all reports!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating reports: {e}'))