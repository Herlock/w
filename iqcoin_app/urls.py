from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('student-login/', views.student_login, name='student_login'),
    # Разрешаем GET-запросы для выхода
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('award-coins/', views.award_coins, name='award_coins'),
    path('deduct-coins/', views.deduct_coins, name='deduct_coins'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('edit-transaction/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    # Student management URLs
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
]