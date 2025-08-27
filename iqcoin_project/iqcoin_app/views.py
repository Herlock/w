from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.db import transaction as db_transaction
from .models import Student, Class, Transaction
from .forms import AwardCoinsForm, DeductCoinsForm, EditTransactionForm, StudentForm, StudentEditForm

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def home(request):
    students = Student.objects.all().order_by('group', 'name')
    recent_transactions = Transaction.objects.all().order_by('-date')[:10]
    context = {
        'students': students,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'home.html', context)

@login_required
def award_coins(request):
    if request.method == 'POST':
        form = AwardCoinsForm(request.POST)
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
        form = AwardCoinsForm()
    
    return render(request, 'award_coins.html', {'form': form})

@login_required
def deduct_coins(request):
    if request.method == 'POST':
        form = DeductCoinsForm(request.POST)
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
        form = DeductCoinsForm()
    
    return render(request, 'deduct_coins.html', {'form': form})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.all().order_by('-date')
    
    # Filter by student if specified
    student_filter = request.GET.get('student')
    if student_filter:
        transactions = transactions.filter(student_id=student_filter)
    
    # Filter by transaction type if specified
    type_filter = request.GET.get('type')
    if type_filter:
        transactions = transactions.filter(type=type_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        transactions = transactions.filter(
            Q(student__name__icontains=search_query) |
            Q(teacher__username__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    students = Student.objects.all().order_by('name')
    
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
    # Filter students by classes taught by the current teacher
    students = Student.objects.filter(group__teacher=request.user).order_by('group', 'name')
    
    # Get search query
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(group__group__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'student_list.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id, group__teacher=request.user)
    
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
            messages.success(request, f'Student "{student.name}" has been created successfully.')
            return redirect('student_list')
    else:
        form = StudentForm(user=request.user)
    
    return render(request, 'student_create.html', {'form': form})

@login_required
def student_edit(request, student_id):
    student = get_object_or_404(Student, id=student_id, group__teacher=request.user)
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            old_balance = student.balance
            updated_student = form.save()
            new_balance = updated_student.balance
            
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
            
            messages.success(request, f'Student "{updated_student.name}" has been updated successfully.')
            return redirect('student_detail', student_id=updated_student.id)
    else:
        form = StudentEditForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'student_edit.html', context)