from django.contrib import admin
from .models import Expense, Income, Category, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'is_default']
    list_filter = ['category_type', 'is_default']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date']
    list_filter = ['category', 'date']

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'source', 'date']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'theme']
