from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Expense, Income, Category, UserProfile
from .forms import (CustomUserCreationForm, CustomAuthenticationForm,
                    ExpenseForm, IncomeForm, CategoryForm, UserProfileForm)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# ─── Auth Views ───────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_profile(user)
            _seed_default_categories(user)
            login(request, user)
            messages.success(request, f'Welcome to SpendWise Pro, {user.first_name or user.username}! 🎉')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 👋')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def _seed_default_categories(user):
    """Create default categories for a new user"""
    defaults = [
        ('Food & Dining', 'fa-utensils', '#EF4444', 'expense'),
        ('Transportation', 'fa-car', '#F59E0B', 'expense'),
        ('Shopping', 'fa-shopping-bag', '#8B5CF6', 'expense'),
        ('Bills & Utilities', 'fa-bolt', '#EC4899', 'expense'),
        ('Entertainment', 'fa-film', '#06B6D4', 'expense'),
        ('Health & Medical', 'fa-heartbeat', '#10B981', 'expense'),
        ('Travel', 'fa-plane', '#3B82F6', 'expense'),
        ('Education', 'fa-graduation-cap', '#6366F1', 'expense'),
        ('Salary', 'fa-briefcase', '#10B981', 'income'),
        ('Freelance', 'fa-laptop', '#2563EB', 'income'),
        ('Investment', 'fa-chart-line', '#F59E0B', 'income'),
        ('Other', 'fa-ellipsis-h', '#6B7280', 'both'),
    ]
    for name, icon, color, ctype in defaults:
        Category.objects.get_or_create(
            name=name, user=user,
            defaults={'icon': icon, 'color': color, 'category_type': ctype, 'is_default': False}
        )


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    profile = get_or_create_profile(user)
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Totals
    total_expenses = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_income = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expenses

    # This month
    month_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    month_income = Income.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Recent transactions (combined)
    recent_expenses = list(Expense.objects.filter(user=user).select_related('category')[:5])
    recent_income = list(Income.objects.filter(user=user)[:5])

    # Merge and sort by date
    transactions = []
    for e in recent_expenses:
        transactions.append({
            'type': 'expense', 'amount': e.amount,
            'label': e.category.name if e.category else 'Uncategorized',
            'icon': e.category.icon if e.category else 'fa-tag',
            'color': e.category.color if e.category else '#6B7280',
            'date': e.date, 'description': e.description or '',
            'id': e.id
        })
    for i in recent_income:
        transactions.append({
            'type': 'income', 'amount': i.amount,
            'label': i.source, 'icon': 'fa-arrow-up',
            'color': '#10B981', 'date': i.date,
            'description': i.description or '', 'id': i.id
        })
    transactions.sort(key=lambda x: x['date'], reverse=True)
    transactions = transactions[:8]

    # Monthly chart data (last 6 months)
    chart_labels = []
    chart_expenses = []
    chart_income = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=30 * i)
        m, y = d.month, d.year
        chart_labels.append(d.strftime('%b %Y'))
        exp = Expense.objects.filter(user=user, date__month=m, date__year=y).aggregate(t=Sum('amount'))['t'] or 0
        inc = Income.objects.filter(user=user, date__month=m, date__year=y).aggregate(t=Sum('amount'))['t'] or 0
        chart_expenses.append(float(exp))
        chart_income.append(float(inc))

    # Category pie chart
    cat_data = Expense.objects.filter(user=user).values(
        'category__name', 'category__color'
    ).annotate(total=Sum('amount')).order_by('-total')[:6]
    pie_labels = [d['category__name'] or 'Uncategorized' for d in cat_data]
    pie_values = [float(d['total']) for d in cat_data]
    pie_colors = [d['category__color'] or '#6B7280' for d in cat_data]

    # Budget progress
    budget = float(profile.monthly_budget) if profile.monthly_budget else 0
    budget_used_pct = min(int((float(month_expenses) / budget * 100) if budget > 0 else 0), 100)

    context = {
        'profile': profile,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'balance': balance,
        'month_expenses': month_expenses,
        'month_income': month_income,
        'transactions': transactions,
        'chart_labels': json.dumps(chart_labels),
        'chart_expenses': json.dumps(chart_expenses),
        'chart_income': json.dumps(chart_income),
        'pie_labels': json.dumps(pie_labels),
        'pie_values': json.dumps(pie_values),
        'pie_colors': json.dumps(pie_colors),
        'budget': budget,
        'budget_used_pct': budget_used_pct,
        'month_expenses_float': float(month_expenses),
        'currency': profile.currency,
    }
    return render(request, 'tracker/dashboard.html', context)


# ─── Expenses ─────────────────────────────────────────────────────────────────

@login_required
def expense_list(request):
    user = request.user
    profile = get_or_create_profile(user)
    qs = Expense.objects.filter(user=user).select_related('category')

    # Filters
    category_filter = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    if category_filter:
        qs = qs.filter(category__id=category_filter)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if search:
        qs = qs.filter(Q(description__icontains=search) | Q(category__name__icontains=search))

    total = qs.aggregate(total=Sum('amount'))['total'] or 0
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.filter(Q(user=user) | Q(is_default=True))

    return render(request, 'tracker/expense_list.html', {
        'page_obj': page, 'total': total, 'categories': categories,
        'category_filter': category_filter, 'date_from': date_from,
        'date_to': date_to, 'search': search, 'profile': profile,
    })


@login_required
def add_expense(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, '✅ Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(request.user)
    return render(request, 'tracker/expense_form.html', {
        'form': form, 'title': 'Add Expense', 'profile': profile,
    })


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(request.user, instance=expense)
    return render(request, 'tracker/expense_form.html', {
        'form': form, 'title': 'Edit Expense', 'expense': expense, 'profile': profile,
    })


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, '🗑️ Expense deleted.')
        return redirect('expense_list')
    return render(request, 'tracker/confirm_delete.html', {'obj': expense, 'type': 'Expense'})


# ─── Income ───────────────────────────────────────────────────────────────────

@login_required
def income_list(request):
    user = request.user
    profile = get_or_create_profile(user)
    qs = Income.objects.filter(user=user)

    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        qs = qs.filter(Q(source__icontains=search) | Q(description__icontains=search))
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    total = qs.aggregate(total=Sum('amount'))['total'] or 0
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'tracker/income_list.html', {
        'page_obj': page, 'total': total, 'search': search,
        'date_from': date_from, 'date_to': date_to, 'profile': profile,
    })


@login_required
def add_income(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, '✅ Income added successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm(request.user)
    return render(request, 'tracker/income_form.html', {
        'form': form, 'title': 'Add Income', 'profile': profile,
    })


@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Income updated successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm(request.user, instance=income)
    return render(request, 'tracker/income_form.html', {
        'form': form, 'title': 'Edit Income', 'income': income, 'profile': profile,
    })


@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, '🗑️ Income deleted.')
        return redirect('income_list')
    return render(request, 'tracker/confirm_delete.html', {'obj': income, 'type': 'Income'})


# ─── Categories ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    profile = get_or_create_profile(request.user)
    from django.db.models import Q
    categories = Category.objects.filter(Q(user=request.user) | Q(is_default=True))
    return render(request, 'tracker/category_list.html', {'categories': categories, 'profile': profile})


@login_required
def add_category(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, '✅ Category created!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'tracker/category_form.html', {'form': form, 'profile': profile})


@login_required
def delete_category(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, '🗑️ Category deleted.')
        return redirect('category_list')
    return render(request, 'tracker/confirm_delete.html', {'obj': cat, 'type': 'Category'})


# ─── Reports ──────────────────────────────────────────────────────────────────

@login_required
def reports(request):
    user = request.user
    profile = get_or_create_profile(user)
    now = timezone.now()

    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    # Monthly breakdown
    monthly_data = []
    for m in range(1, 13):
        exp = Expense.objects.filter(user=user, date__year=year, date__month=m).aggregate(t=Sum('amount'))['t'] or 0
        inc = Income.objects.filter(user=user, date__year=year, date__month=m).aggregate(t=Sum('amount'))['t'] or 0
        monthly_data.append({
            'month': datetime(year, m, 1).strftime('%b'),
            'expenses': float(exp), 'income': float(inc),
            'net': float(inc) - float(exp)
        })

    # Category breakdown for selected month
    cat_breakdown = Expense.objects.filter(
        user=user, date__year=year, date__month=month
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')

    yearly_expense = Expense.objects.filter(user=user, date__year=year).aggregate(t=Sum('amount'))['t'] or 0
    yearly_income = Income.objects.filter(user=user, date__year=year).aggregate(t=Sum('amount'))['t'] or 0

    years = list(range(now.year - 3, now.year + 1))

    context = {
        'profile': profile,
        'monthly_data': json.dumps(monthly_data),
        'monthly_data_raw': monthly_data,
        'cat_breakdown': cat_breakdown,
        'yearly_expense': yearly_expense,
        'yearly_income': yearly_income,
        'year': year, 'month': month,
        'years': years,
        'months': [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        'currency': profile.currency,
    }
    return render(request, 'tracker/reports.html', context)


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    profile = get_or_create_profile(user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })

    # Stats
    total_expenses = Expense.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or 0
    total_income = Income.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or 0
    expense_count = Expense.objects.filter(user=user).count()

    return render(request, 'tracker/profile.html', {
        'form': form, 'profile': profile,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'expense_count': expense_count,
    })


# ─── Landing Page ─────────────────────────────────────────────────────────────

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


# ─── AJAX: Toggle Theme ───────────────────────────────────────────────────────

@login_required
def toggle_theme(request):
    if request.method == 'POST':
        profile = get_or_create_profile(request.user)
        profile.theme = 'dark' if profile.theme == 'light' else 'light'
        profile.save()
        return JsonResponse({'theme': profile.theme})
    return JsonResponse({'error': 'POST required'}, status=400)
