from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.db import transaction as db_transaction
from django.http import HttpResponseForbidden
from .models import Student, Transaction, UserProfile
from .forms import AwardCoinsForm, DeductCoinsForm, EditTransactionForm, StudentForm, StudentEditForm
from .decorators import student_required, teacher_required, admin_required, teacher_or_admin_required, role_required

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check user role and redirect accordingly
            try:
                user_profile = user.userprofile
            except UserProfile.DoesNotExist:
                # Create a default profile if it doesn't exist
                user_profile = UserProfile.objects.create(user=user, role='teacher')
            
            # Redirect based on role
            if user_profile.role == 'student':
                return redirect('home')  # Will show student home
            elif user_profile.role == 'teacher':
                return redirect('home')  # Will show teacher home
            elif user_profile.role == 'admin':
                return redirect('home')  # Will show admin home
            else:
                return redirect('home')  # Default home
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def student_login(request):
    """
    Custom login view for students using phone number.
    Students don't need a password, just their phone number.
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        if phone_number:
            # Use our custom authentication backend
            user = authenticate(request, phone_number=phone_number)
            if user is not None:
                login(request, user)
                return redirect('home')  # Will show student home
            else:
                messages.error(request, 'Invalid phone number or student not found.')
        else:
            messages.error(request, 'Please enter your phone number.')
    
    return render(request, 'student_login.html')

def custom_logout(request):
    """
    Custom logout view that properly clears session and redirects to student login.
    """
    # Clear the student phone number from session
    if 'student_phone_number' in request.session:
        del request.session['student_phone_number']
    
    # Logout the user
    logout(request)
    
    # Redirect to student login page
    return redirect('student_login')

@login_required
def home(request):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Check if this is a student
    if user_profile.role == 'student':
        # Get the phone number from session (set during login)
        phone_number = request.session.get('student_phone_number')
        
        if phone_number:
            # Get all students with this phone number
            students_with_phone = Student.objects.filter(
                phone_number=phone_number,
                is_active=True
            ).order_by('name')
            
            # Get all transactions for these students
            recent_transactions = Transaction.objects.filter(
                student__in=students_with_phone
            ).order_by('-date')[:10]
            
            context = {
                'students': students_with_phone,
                'recent_transactions': recent_transactions,
                'phone_number': phone_number,
            }
            return render(request, 'student_home.html', context)
    
    # For teachers and admins, redirect to student list
    return redirect('student_list')

@login_required
def award_coins(request):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Only teachers and admins can award coins
    if user_profile.role not in ['teacher', 'admin']:
        return HttpResponseForbidden("Only teachers and admins can award coins.")
    
    if request.method == 'POST':
        form = AwardCoinsForm(request.POST, user=request.user)
        if form.is_valid():
            students = form.cleaned_data['students']
            amount = form.cleaned_data['amount']
            
            with db_transaction.atomic():
                for student in students:
                    # Create transaction record
                    Transaction.objects.create(
                        type='AWARD',
                        amount=amount,
                        student=student,
                        teacher=request.user
                    )
                    # Update student balance
                    student.balance += amount
                    student.save()
            
            messages.success(request, f'Successfully awarded {amount} IQ-coins to {students.count()} students.')
            return redirect('home')
    else:
        form = AwardCoinsForm(user=request.user)
    
    return render(request, 'award_coins.html', {'form': form})

@login_required
def deduct_coins(request):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Only teachers and admins can deduct coins
    if user_profile.role not in ['teacher', 'admin']:
        return HttpResponseForbidden("Only teachers and admins can deduct coins.")
    
    if request.method == 'POST':
        form = DeductCoinsForm(request.POST, user=request.user)
        if form.is_valid():
            student = form.cleaned_data['student']
            amount = form.cleaned_data['amount']
            comment = form.cleaned_data['comment']
            
            if student.balance >= amount:
                with db_transaction.atomic():
                    # Create transaction record
                    Transaction.objects.create(
                        type='DEDUCT',
                        amount=amount,
                        student=student,
                        teacher=request.user,
                        comment=comment
                    )
                    # Update student balance
                    student.balance -= amount
                    student.save()
                
                messages.success(request, f'Successfully deducted {amount} IQ-coins from {student.name}.')
                return redirect('home')
            else:
                messages.error(request, f'{student.name} has insufficient balance. Current balance: {student.balance}')
    else:
        form = DeductCoinsForm(user=request.user)
    
    return render(request, 'deduct_coins.html', {'form': form})

@login_required
def transaction_history(request):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Role-based access
    if user_profile.role == 'student':
        # Students can see transactions for all students with their phone number
        phone_number = request.session.get('student_phone_number')
        if phone_number:
            # Get all students with this phone number
            students_with_phone = Student.objects.filter(
                phone_number=phone_number,
                is_active=True
            )
            transactions = Transaction.objects.filter(student__in=students_with_phone).order_by('-date')
        else:
            # Fallback to just their own transactions
            transactions = Transaction.objects.filter(student=user_profile.student).order_by('-date') if user_profile.student else Transaction.objects.none()
    elif user_profile.role == 'teacher':
        # Teachers can only see transactions they made
        transactions = Transaction.objects.filter(teacher=request.user).order_by('-date')
    elif user_profile.role == 'admin':
        # Admins can see all transactions
        transactions = Transaction.objects.all().order_by('-date')
    else:
        # Default: teachers can only see transactions they made
        transactions = Transaction.objects.filter(teacher=request.user).order_by('-date')
    
    # Filter by student if specified (only for teachers and admins)
    student_filter = request.GET.get('student')
    if student_filter and user_profile.role in ['teacher', 'admin']:
        transactions = transactions.filter(student_id=student_filter)
    
    # Filter by transaction type if specified
    type_filter = request.GET.get('type')
    if type_filter:
        transactions = transactions.filter(type=type_filter)
    
    # Search functionality (only for teachers and admins)
    search_query = request.GET.get('search')
    if search_query and user_profile.role in ['teacher', 'admin']:
        transactions = transactions.filter(
            Q(student__name__icontains=search_query) |
            Q(teacher__username__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    # Get students for filter dropdown (only for teachers and admins)
    if user_profile.role in ['teacher', 'admin']:
        students = Student.objects.all().order_by('name')
    else:
        students = Student.objects.none()
    
    context = {
        'transactions': transactions,
        'students': students,
        'current_student': student_filter,
        'current_type': type_filter,
        'search_query': search_query,
    }
    return render(request, 'transaction_history.html', context)

@login_required
def edit_transaction(request, transaction_id):
    trans = get_object_or_404(Transaction, id=transaction_id)
    
    # Only allow editing award transactions
    if trans.type != 'AWARD':
        messages.error(request, 'Only award transactions can be edited.')
        return redirect('transaction_history')
    
    if request.method == 'POST':
        form = EditTransactionForm(request.POST, instance=trans)
        if form.is_valid():
            old_amount = trans.amount
            new_amount = form.cleaned_data['amount']
            
            with db_transaction.atomic():
                # Update student balance
                difference = new_amount - old_amount
                trans.student.balance += difference
                trans.student.save()
                
                # Save transaction with edited flag
                trans.amount = new_amount
                trans.edited = True
                trans.save()
            
            messages.success(request, f'Transaction updated successfully. Balance adjusted by {difference} coins.')
            return redirect('transaction_history')
    else:
        form = EditTransactionForm(instance=trans)
    
    return render(request, 'edit_transaction.html', {'form': form, 'transaction': trans})

@login_required
def student_list(request):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Role-based access
    if user_profile.role == 'student':
        # Students can only see themselves
        students = Student.objects.filter(id=user_profile.student.id) if user_profile.student else Student.objects.none()
    elif user_profile.role == 'teacher':
        # Teachers can only see their own students (all students, including hidden - this is the management page)
        students = Student.objects.filter(teacher=request.user).order_by('name')
    elif user_profile.role == 'admin':
        # Admins can see all students (including hidden - this is the management page)
        students = Student.objects.all().order_by('teacher__username', 'name')
    else:
        # Default: teachers can only see their own students
        students = Student.objects.filter(teacher=request.user).order_by('name')
    
    # Get search query
    search_query = request.GET.get('search')
    if search_query:
        # Enhanced search for administrators - include phone number and teacher name
        if user_profile.role == 'admin':
            students = students.filter(
                Q(name__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(teacher__username__icontains=search_query) |
                Q(teacher__userprofile__full_name__icontains=search_query)
            )
        else:
            # Regular search for teachers
            students = students.filter(
                Q(name__icontains=search_query)
            )
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'student_list.html', context)

@login_required
def student_detail(request, student_id):
    # Get user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Role-based access
    if user_profile.role == 'student':
        # Students can only see their own details
        if user_profile.student and user_profile.student.id == student_id:
            student = get_object_or_404(Student, id=student_id)
        else:
            return HttpResponseForbidden("You don't have permission to view this student's details.")
    elif user_profile.role == 'teacher':
        # Teachers can only see their own students
        student = get_object_or_404(Student, id=student_id, teacher=request.user)
    elif user_profile.role == 'admin':
        # Admins can see all students
        student = get_object_or_404(Student, id=student_id)
    else:
        # Default: teachers can only see their own students
        student = get_object_or_404(Student, id=student_id, teacher=request.user)
    
    # Get recent transactions for this student
    recent_transactions = Transaction.objects.filter(student=student).order_by('-date')[:10]
    
    context = {
        'student': student,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'student_detail.html', context)

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, user=request.user)
        if form.is_valid():
            student = form.save()
            
            # Create a user account for the student if phone number is provided
            if student.phone_number:
                # Create a unique username for the student
                username = f"student_{student.id}"
                # Create user account (password not needed for student login)
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': student.name,
                        'is_active': True,
                        'is_staff': False,
                        'is_superuser': False
                    }
                )
                
                # Link student to user profile
                profile, profile_created = UserProfile.objects.get_or_create(user=user)
                profile.student = student
                profile.role = 'student'
                profile.save()
            
            messages.success(request, f'Student "{student.name}" has been created successfully.')
            return redirect('student_list')
    else:
        form = StudentForm(user=request.user)
    
    return render(request, 'student_create.html', {'form': form})

@login_required
def student_edit(request, student_id):
    # Get user profile to check permissions
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='teacher')
    
    # Role-based access
    if user_profile.role == 'admin':
        student = get_object_or_404(Student, id=student_id)
    elif user_profile.role == 'teacher':
        student = get_object_or_404(Student, id=student_id, teacher=request.user)
    else:
        return HttpResponseForbidden("You don't have permission to edit students.")
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student, user=request.user)
        if form.is_valid():
            old_balance = student.balance
            old_teacher = student.teacher
            old_phone = student.phone_number
            
            updated_student = form.save()
            new_balance = updated_student.balance
            new_teacher = updated_student.teacher
            new_phone = updated_student.phone_number
            
            # Update associated user account if phone number changed
            if old_phone != new_phone and new_phone:
                # Create or update user account for the student
                username = f"student_{updated_student.id}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': updated_student.name,
                        'is_active': True,
                        'is_staff': False,
                        'is_superuser': False
                    }
                )
                
                # Link student to user profile
                profile, profile_created = UserProfile.objects.get_or_create(user=user)
                profile.student = updated_student
                profile.role = 'student'
                profile.save()
            
            # If balance was changed, create a transaction record
            if old_balance != new_balance:
                balance_difference = new_balance - old_balance
                transaction_type = 'AWARD' if balance_difference > 0 else 'DEDUCT'
                Transaction.objects.create(
                    type=transaction_type,
                    amount=abs(balance_difference),
                    student=updated_student,
                    teacher=request.user,
                    comment=f'Balance manually adjusted from {old_balance} to {new_balance}'
                )
            
            # If teacher was changed, add a comment about the transfer
            if old_teacher != new_teacher:
                messages.info(request, f'Student transferred from "{old_teacher.username}" to "{new_teacher.username}".')
            
            messages.success(request, f'Student "{updated_student.name}" has been updated successfully.')
            return redirect('student_detail', student_id=updated_student.id)
    else:
        form = StudentEditForm(instance=student, user=request.user)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'student_edit.html', context)