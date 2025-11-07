from django import forms
from .models import Student, Transaction
from django.contrib.auth.models import User

class AwardCoinsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), widget=forms.CheckboxSelectMultiple)
    amount = forms.IntegerField(min_value=1, label="IQ-coins (1-3)")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Check if user is admin
            try:
                user_profile = user.userprofile
                if user_profile.role == 'admin':
                    # Admins can award coins to all students
                    # Exclude hidden students from award form
                    self.fields['students'].queryset = Student.objects.filter(is_hidden=False)
                else:
                    # Teachers can only award coins to their own students
                    # Exclude hidden students from award form
                    self.fields['students'].queryset = Student.objects.filter(teacher=user, is_hidden=False)
            except:
                # Default: only show students from classes taught by the current teacher
                # Exclude hidden students from award form
                self.fields['students'].queryset = Student.objects.filter(teacher=user, is_hidden=False)

class DeductCoinsForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.none(), label="Student")
    amount = forms.IntegerField(min_value=1, label="Amount")
    comment = forms.CharField(widget=forms.Textarea, required=True, label="Comment")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Check if user is admin
            try:
                user_profile = user.userprofile
                if user_profile.role == 'admin':
                    # Admins can deduct coins from all students
                    # Exclude hidden students from deduct form
                    self.fields['student'].queryset = Student.objects.filter(is_hidden=False)
                else:
                    # Teachers can only deduct coins from their own students
                    # Exclude hidden students from deduct form
                    self.fields['student'].queryset = Student.objects.filter(teacher=user, is_hidden=False)
            except:
                # Default: only show students from classes taught by the current teacher
                # Exclude hidden students from deduct form
                self.fields['student'].queryset = Student.objects.filter(teacher=user, is_hidden=False)

class EditTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 1, 'max': 3}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'teacher', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number (e.g., +79991234567)'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Check if user is admin
            try:
                user_profile = user.userprofile
                if user_profile.role == 'admin':
                    # Admins can assign students to any teacher
                    self.fields['teacher'].queryset = User.objects.filter(userprofile__role__in=['teacher', 'admin'])
                else:
                    # Teachers can only create students for themselves
                    self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                    self.fields['teacher'].initial = user
                    self.fields['teacher'].widget = forms.HiddenInput()
            except:
                # Default: only show current user
                self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                self.fields['teacher'].initial = user
                self.fields['teacher'].widget = forms.HiddenInput()

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'teacher', 'balance', 'phone_number', 'is_active', 'is_hidden']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number (e.g., +79991234567)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_hidden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Student Name',
            'teacher': 'Teacher',
            'balance': 'IQ-coin Balance',
            'phone_number': 'Phone Number',
            'is_active': 'Active Student',
            'is_hidden': 'Hide from General Lists',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Check if user is admin
            try:
                user_profile = user.userprofile
                if user_profile.role == 'admin':
                    # Admins can assign students to any teacher
                    self.fields['teacher'].queryset = User.objects.filter(userprofile__role__in=['teacher', 'admin'])
                else:
                    # Teachers can only assign to themselves
                    self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                    self.fields['teacher'].widget = forms.HiddenInput()
            except:
                # Default: only show current user
                self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                self.fields['teacher'].widget = forms.HiddenInput()

