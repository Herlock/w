from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from iqcoin_app.models import UserProfile

class Command(BaseCommand):
    help = 'Set full names for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-fullnames',
            nargs='+',
            type=str,
            help='Username and full name pairs in format username:"Full Name"',
        )

    def handle(self, *args, **options):
        if options['user_fullnames']:
            for user_fullname in options['user_fullnames']:
                if ':' in user_fullname:
                    username, full_name = user_fullname.split(':', 1)
                    try:
                        user = User.objects.get(username=username)
                        profile, created = UserProfile.objects.get_or_create(user=user)
                        profile.full_name = full_name
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully set full name "{full_name}" for user {username}'
                            )
                        )
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f'User {username} does not exist'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Invalid format for "{user_fullname}". Use username:"Full Name"'
                        )
                    )