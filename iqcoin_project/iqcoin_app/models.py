from django.db import models
from django.contrib.auth.models import User

class Class(models.Model):
    group = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.group}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Class, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.group.group})"

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