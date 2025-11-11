from django.db import models
from django.contrib.auth.models import User

# Define user roles
USER_ROLES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('admin', 'Admin'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='teacher')
    # For students, we can link to a specific student record
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True)
    # Full name for better identification
    full_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')
    balance = models.IntegerField(default=0)
    # Phone number for student login (can be shared by multiple students, e.g., siblings)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # Flag to indicate if student account is active
    is_active = models.BooleanField(default=True)
    # Flag to hide student from general lists (home page, award/deduct forms)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (Teacher: {self.teacher.username})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('AWARD', 'Award'),
        ('DEDUCT', 'Deduction'),
    )
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} {self.amount} for {self.student} by {self.teacher}"