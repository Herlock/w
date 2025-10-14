from django import forms
from .models import Class, Student, Transaction

class AwardCoinsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), widget=forms.CheckboxSelectMultiple)
    amount = forms.IntegerField(min_value=1, label="IQ-coins (1-3)")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show students from classes taught by the current teacher
            self.fields['students'].queryset = Student.objects.filter(group__teacher=user)

class DeductCoinsForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.none(), label="Student")
    amount = forms.IntegerField(min_value=1, label="Amount")
    comment = forms.CharField(widget=forms.Textarea, required=True, label="Comment")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show students from classes taught by the current teacher
            self.fields['student'].queryset = Student.objects.filter(group__teacher=user)

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
        fields = ['name', 'group', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number (e.g., +79991234567)'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show classes that belong to the current teacher
            self.fields['group'].queryset = Class.objects.filter(teacher=user)

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'group', 'balance', 'phone_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number (e.g., +79991234567)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Student Name',
            'group': 'Class/Group',
            'balance': 'IQ-coin Balance',
            'phone_number': 'Phone Number',
            'is_active': 'Active Student',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show classes that belong to the current teacher
            self.fields['group'].queryset = Class.objects.filter(teacher=user)

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['group', 'description']
        widgets = {
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class/group name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }
        labels = {
            'group': 'Class/Group Name',
            'description': 'Description',
        }

class ClassEditForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['group', 'description']
        widgets = {
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class/group name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }
        labels = {
            'group': 'Class/Group Name',
            'description': 'Description',
        }