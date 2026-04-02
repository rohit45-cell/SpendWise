from django.urls import path
from . import views

urlpatterns = [
    # Landing
    path('', views.landing, name='landing'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    # Income
    path('income/', views.income_list, name='income_list'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # API
    path('api/toggle-theme/', views.toggle_theme, name='toggle_theme'),
]
