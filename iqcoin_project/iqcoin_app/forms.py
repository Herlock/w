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