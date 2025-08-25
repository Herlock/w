from django.contrib import admin
from .models import Student, Class, Transaction

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'balance')
    list_filter = ('group',)
    search_fields = ('name',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('group', 'teacher')
    list_filter = ('group', 'teacher')
    search_fields = ('group',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'student', 'teacher', 'date', 'edited')
    list_filter = ('type', 'student', 'teacher', 'date')
    search_fields = ('student__name', 'teacher__username')