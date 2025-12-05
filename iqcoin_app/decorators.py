from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import UserProfile, Student

def role_required(allowed_roles):
    """
    Decorator that checks if the user has one of the allowed roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has a profile
            try:
                user_profile = request.user.userprofile
            except UserProfile.DoesNotExist:
                # Check if this is a student user account (created by the StudentPhoneBackend)
                if request.user.username.startswith('student_'):
                    # This is a student user account
                    # Determine if it's a parent (multiple students with same phone) or student
                    try:
                        student = Student.objects.get(id=int(request.user.username.split('_')[1]))
                        # Count how many students share this phone number
                        phone_number = student.phone_number
                        if phone_number:
                            student_count = Student.objects.filter(phone_number=phone_number, is_active=True).count()
                            role = 'parent' if student_count > 1 else 'student'
                        else:
                            role = 'student'
                        user_profile = UserProfile.objects.create(user=request.user, role=role, student=student)
                    except (ValueError, Student.DoesNotExist):
                        # Fallback to student role if we can't determine
                        user_profile = UserProfile.objects.create(user=request.user, role='student')
                # But don't assume it's a teacher - let's check if it's linked to a student
                elif hasattr(request.user, 'student_set') and request.user.student_set.exists():
                    # This user is linked to a student, so they should be a student or parent
                    student_count = request.user.student_set.count()
                    role = 'parent' if student_count > 1 else 'student'
                    user_profile = UserProfile.objects.create(user=request.user, role=role)
                else:
                    # Default to teacher for staff/admin users
                    user_profile = UserProfile.objects.create(user=request.user, role='teacher')
            
            # Check if user has one of the allowed roles
            if user_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        
        return _wrapped_view
    return decorator

def student_required(view_func):
    """
    Decorator that allows only students to access the view.
    """
    return role_required(['student'])(view_func)

def teacher_required(view_func):
    """
    Decorator that allows only teachers to access the view.
    """
    return role_required(['teacher'])(view_func)

def admin_required(view_func):
    """
    Decorator that allows only admins to access the view.
    """
    return role_required(['admin'])(view_func)

def teacher_or_admin_required(view_func):
    """
    Decorator that allows only teachers or admins to access the view.
    """
    return role_required(['teacher', 'admin'])(view_func)