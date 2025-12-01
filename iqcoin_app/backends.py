from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Student, UserProfile

class StudentPhoneBackend(BaseBackend):
    """
    Custom authentication backend for student login via phone number.
    Students don't need a password, they just enter their phone number.
    """
    
    def authenticate(self, request, phone_number=None, **kwargs):
        """
        Authenticate a student by phone number.
        Returns a User object if authentication is successful, None otherwise.
        """
        if phone_number is None:
            return None
            
        try:
            # Find students by phone number (may be multiple students sharing the same number)
            students = Student.objects.filter(phone_number=phone_number, is_active=True)
            
            if not students.exists():
                return None
            
            # Check if this phone number is shared by multiple students (parent login)
            is_parent = students.count() > 1
            
            # Use the first student to create/get the user account
            # All students with this phone number will be shown on the home page
            student = students.first()
            
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
            
            # Link the student to the user profile
            profile, profile_created = UserProfile.objects.get_or_create(user=user)
            # Always ensure the student is linked and role is correctly set
            profile.student = student
            # Assign parent role if multiple students share this phone number
            profile.role = 'parent' if is_parent else 'student'
            profile.save()
            
            # Store the phone number in the session so we can show all students with this phone
            if request:
                request.session['student_phone_number'] = phone_number
            
            return user
        except Exception as e:
            # Log the error for debugging
            print(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get a user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None