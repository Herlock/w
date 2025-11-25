from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # But don't assume it's a teacher - let's check if it's linked to a student
        if hasattr(instance, 'student_set') and instance.student_set.exists():
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