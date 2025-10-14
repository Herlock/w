from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import UserProfile

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
                # If no profile exists, create one with default teacher role
                user_profile = UserProfile.objects.create(user=request.user, role='teacher')
            
            # Check if user's role is in allowed roles
            if user_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Return forbidden response or redirect to appropriate page
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