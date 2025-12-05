from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('student-login/', views.student_login, name='student_login'),
    # Custom logout view to properly clear session
    path('logout/', views.custom_logout, name='logout'),
    path('award-coins/', views.award_coins, name='award_coins'),
    path('deduct-coins/', views.deduct_coins, name='deduct_coins'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('edit-transaction/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    # Student management URLs
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    # Robots.txt handler
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]