from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Student

class StudentPhoneBackend(BaseBackend):
    """
    Custom authentication backend for student login via phone number.
    Students don't need a password, they just enter their phone number.
    """
    
    def authenticate(self, request, phone_number=None):
        """
        Authenticate a student by phone number.
        Returns a User object if authentication is successful, None otherwise.
        """
        if phone_number is None:
            return None
            
        try:
            # Find student by phone number
            student = Student.objects.get(phone_number=phone_number, is_active=True)
            
            # Create or get a user object for this student
            # We'll use a prefix to distinguish student users from regular users
            username = f"student_{student.id}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': student.name,
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            # Link the student to the user profile if not already linked
            from .models import UserProfile
            profile, profile_created = UserProfile.objects.get_or_create(user=user)
            if not profile.student:
                profile.student = student
                profile.role = 'student'
                profile.save()
            
            return user
        except Student.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """
        Get a user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None