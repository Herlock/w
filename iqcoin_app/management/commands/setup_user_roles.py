from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from iqcoin_app.models import UserProfile

class Command(BaseCommand):
    help = 'Set up user roles for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-usernames',
            nargs='+',
            type=str,
            help='Usernames of users to set as admins',
        )
        parser.add_argument(
            '--teacher-usernames',
            nargs='+',
            type=str,
            help='Usernames of users to set as teachers',
        )
        parser.add_argument(
            '--student-usernames',
            nargs='+',
            type=str,
            help='Usernames of users to set as students',
        )

    def handle(self, *args, **options):
        # Set admins
        if options['admin_usernames']:
            for username in options['admin_usernames']:
                try:
                    user = User.objects.get(username=username)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = 'admin'
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully set {username} as admin'
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'User {username} does not exist'
                        )
                    )

        # Set teachers
        if options['teacher_usernames']:
            for username in options['teacher_usernames']:
                try:
                    user = User.objects.get(username=username)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = 'teacher'
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully set {username} as teacher'
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'User {username} does not exist'
                        )
                    )

        # Set students
        if options['student_usernames']:
            for username in options['student_usernames']:
                try:
                    user = User.objects.get(username=username)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = 'student'
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully set {username} as student'
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'User {username} does not exist'
                        )
                    )

        # For all other users, set as teachers by default
        all_users = User.objects.all()
        for user in all_users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.role = 'teacher'
                profile.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created profile for {user.username} as teacher (default)'
                    )
                )