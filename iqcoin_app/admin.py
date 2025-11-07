from django.contrib import admin
from .models import Student, Transaction, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'student', 'full_name')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'full_name')
    fields = ('user', 'role', 'student', 'full_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'balance', 'is_hidden')
    list_filter = ('teacher', 'is_hidden')
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'student', 'teacher', 'date', 'edited')
    list_filter = ('type', 'student', 'teacher', 'date')
    search_fields = ('student__name', 'teacher__username')