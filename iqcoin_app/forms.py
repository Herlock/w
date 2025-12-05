from django import forms
from .models import Student, Transaction
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class StudentWithTeacherWidget(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # Convert value to integer if it's a ModelChoiceIteratorValue
                if hasattr(value, 'value'):
                    student_id = value.value
                else:
                    student_id = value
                    
                if student_id and str(student_id).isdigit():
                    student = Student.objects.select_related('teacher__userprofile').get(pk=student_id)
                    # Try to get the teacher's full name, fallback to username
                    if student.teacher:
                        if hasattr(student.teacher, 'userprofile') and student.teacher.userprofile.full_name:
                            teacher_name = student.teacher.userprofile.full_name
                        else:
                            teacher_name = student.teacher.username
                        # Add the teacher name as a data attribute (using underscore instead of hyphen)
                        option['attrs']['data_teacher_name'] = teacher_name
                        # Add the teacher ID as a data attribute
                        option['attrs']['data_teacher_id'] = student.teacher.id
            except (Student.DoesNotExist, AttributeError):
                pass
        return option
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        # Add JavaScript to format the display and make entire cell clickable
        js_code = '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Format student items to show teacher name in smaller font
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name="%s"]');
            checkboxes.forEach(function(checkbox) {
                // Get the parent element (the label container)
                const parent = checkbox.closest('.form-check');
                // Get the student-item container (the block with padding)
                const studentItem = checkbox.closest('.student-item');
                if (parent && studentItem) {
                    // Get the label element
                    const label = parent.querySelector('label');
                    if (label) {
                        // Get the student name (current text)
                        const studentName = label.textContent.trim();
                        
                        // Get the teacher name from data attribute (using underscore instead of hyphen)
                        const teacherName = checkbox.getAttribute('data_teacher_name');
                        
                        if (teacherName) {
                            // Update the label to show student name and teacher name separately
                            label.innerHTML = studentName + ' <small class="text-muted">(' + teacherName + ')</small>';
                        }
                        
                        // Make the entire student-item container clickable
                        studentItem.style.cursor = 'pointer';
                        studentItem.addEventListener('click', function(e) {
                            // Don't trigger if clicking on the checkbox itself or the label
                            if (e.target !== checkbox && e.target !== label) {
                                checkbox.checked = !checkbox.checked;
                                // Trigger change event
                                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        });
                        
                        // Also make the label clickable to toggle the checkbox
                        label.style.cursor = 'pointer';
                        label.addEventListener('click', function(e) {
                            e.preventDefault();
                            checkbox.checked = !checkbox.checked;
                            // Trigger change event
                            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        });
                    }
                }
            });
        });
        </script>
        ''' % name
        return mark_safe(html + js_code)

class AwardCoinsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), widget=StudentWithTeacherWidget, label="Выберите учеников")
    amount = forms.IntegerField(min_value=1, label="Количество Айкьюшек (1-3)")
    
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
                    # Order by teacher username, then by student name
                    self.fields['students'].queryset = Student.objects.filter(is_hidden=False).select_related('teacher__userprofile').order_by('teacher__username', 'name')
                else:
                    # Teachers can only award coins to their own students
                    # Exclude hidden students from award form
                    # Order by student name
                    self.fields['students'].queryset = Student.objects.filter(teacher=user, is_hidden=False).order_by('name')
            except:
                # Default: only show students from classes taught by the current teacher
                # Exclude hidden students from award form
                # Order by student name
                self.fields['students'].queryset = Student.objects.filter(teacher=user, is_hidden=False).order_by('name')

class DeductCoinsForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.none(), label="Ученик")
    amount = forms.IntegerField(min_value=1, label="Количество")
    comment = forms.CharField(widget=forms.Textarea, required=True, label="Комментарий")
    
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
                    # Order students alphabetically by name
                    self.fields['student'].queryset = Student.objects.filter(is_hidden=False).order_by('name')
                else:
                    # Teachers can only deduct coins from their own students
                    # Exclude hidden students from deduct form
                    # Order students alphabetically by name
                    self.fields['student'].queryset = Student.objects.filter(teacher=user, is_hidden=False).order_by('name')
            except:
                # Default: only show students from classes taught by the current teacher
                # Exclude hidden students from deduct form
                # Order students alphabetically by name
                self.fields['student'].queryset = Student.objects.filter(teacher=user, is_hidden=False).order_by('name')

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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя ученика'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона (например, +79991234567)'}),
        }
        labels = {
            'name': 'Имя ученика',
            'teacher': 'Педагог',
            'phone_number': 'Номер телефона',
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
                    teacher_queryset = User.objects.filter(userprofile__role__in=['teacher', 'admin'])
                    # Update the queryset to show full names
                    self.fields['teacher'].queryset = teacher_queryset
                    self.fields['teacher'].choices = [
                        (teacher.id, teacher.userprofile.full_name if hasattr(teacher, 'userprofile') and teacher.userprofile.full_name else teacher.username)
                        for teacher in teacher_queryset
                    ]
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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя ученика'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона (например, +79991234567)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_hidden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Имя ученика',
            'teacher': 'Педагог',
            'balance': 'Баланс Айкьюшек',
            'phone_number': 'Номер телефона',
            'is_active': 'Активный ученик',
            'is_hidden': 'Скрыть из общих списков',
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
                    teacher_queryset = User.objects.filter(userprofile__role__in=['teacher', 'admin'])
                    # Update the queryset to show full names
                    self.fields['teacher'].queryset = teacher_queryset
                    self.fields['teacher'].choices = [
                        (teacher.id, teacher.userprofile.full_name if hasattr(teacher, 'userprofile') and teacher.userprofile.full_name else teacher.username)
                        for teacher in teacher_queryset
                    ]
                else:
                    # Teachers can only assign to themselves
                    self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                    self.fields['teacher'].widget = forms.HiddenInput()
            except:
                # Default: only show current user
                self.fields['teacher'].queryset = User.objects.filter(id=user.id)
                self.fields['teacher'].widget = forms.HiddenInput()

