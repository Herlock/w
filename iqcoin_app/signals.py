from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Student

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if this is a student user account (created by the StudentPhoneBackend)
        if instance.username.startswith('student_'):
            # This is a student user account
            # Determine if it's a parent (multiple students with same phone) or student
            try:
                student = Student.objects.get(id=int(instance.username.split('_')[1]))
                # Count how many students share this phone number
                phone_number = student.phone_number
                if phone_number:
                    student_count = Student.objects.filter(phone_number=phone_number, is_active=True).count()
                    role = 'parent' if student_count > 1 else 'student'
                else:
                    role = 'student'
                UserProfile.objects.create(user=instance, role=role, student=student)
            except (ValueError, Student.DoesNotExist):
                # Fallback to student role if we can't determine
                UserProfile.objects.create(user=instance, role='student')
        # But don't assume it's a teacher - let's check if it's linked to a student
        elif hasattr(instance, 'student_set') and instance.student_set.exists():
            # This user is linked to a student, so they should be a student or parent
            student_count = instance.student_set.count()
            role = 'parent' if student_count > 1 else 'student'
            UserProfile.objects.create(user=instance, role=role)
        else:
            # Default to teacher for staff/admin users
            UserProfile.objects.create(user=instance, role='teacher')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()