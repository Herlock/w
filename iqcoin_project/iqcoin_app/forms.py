from django import forms
from .models import Class, Student, Transaction

class AwardCoinsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.all(), widget=forms.CheckboxSelectMultiple)
    amount = forms.IntegerField(min_value=1, label="IQ-coins (1-3)")

class DeductCoinsForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label="Student")
    amount = forms.IntegerField(min_value=1, label="Amount")
    comment = forms.CharField(widget=forms.Textarea, required=True, label="Comment")

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
        fields = ['name', 'group']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
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
        fields = ['name', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'name': 'Student Name',
            'balance': 'IQ-coin Balance',
        }