from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .models import Employee, RemoteRequest
from .models import RemoteDay
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import date, datetime, timedelta
from django.core.validators import validate_unicode_slug
from django.core.exceptions import ValidationError
import locale
import holidays

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


def clean_input(input_str):
    try:
        validate_unicode_slug(input_str)
    except ValidationError:
        return ''
    return input_str


def pending_requests_count(user):
    return RemoteRequest.objects.filter(status='pending').count() if user.is_manager else 0


def get_date_range(week_start):
    return [week_start + timedelta(days=i) for i in range(5)]


def update_remote_days(employee, selected_dates, remove, request):
    today = date.today()
    fr_holidays = holidays.France(years=[d.year for d in selected_dates])
    valid_dates = [d for d in selected_dates if d >= today and d not in fr_holidays]
    invalid_dates = [d for d in selected_dates if d < today]
    holiday_dates = [d for d in selected_dates if d in fr_holidays]

    error_message = ''
    if invalid_dates:
        error_message += "Impossible de modifier les jours passés : {}.\n".format(
            ", ".join(str(d) for d in invalid_dates))

    if holiday_dates:
        error_message += "Impossible de modifier les jours fériés : {}.\n".format(
            ", ".join(str(d) for d in holiday_dates))

    if error_message:
        messages.error(request, error_message)
        return False, True  # no valid dates, error occurred

    remote_days_to_update = RemoteDay.objects.filter(date__in=valid_dates)
    employee.remote_days.remove(*remote_days_to_update)
    RemoteRequest.objects.filter(employee=employee, remote_day__in=remote_days_to_update).delete()

    if not remove:
        for selected_date in valid_dates:
            remote_day, created = RemoteDay.objects.get_or_create(date=selected_date)
            employee.remote_days.add(remote_day)
            comment = request.POST.get('comment', '')
            RemoteRequest.objects.get_or_create(employee=employee, remote_day=remote_day, status='pending',
                                                comment=comment)

    return bool(valid_dates), False


@login_required
def setup(request, next_week=0):
    employee = request.user

    if employee.is_superuser:
        return redirect(reverse_lazy('admin:index'))

    today = date.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=next_week)
    date_range = get_date_range(week_start)

    if request.method == 'POST':
        selected_date_strings = request.POST.getlist('remote_days')
        selected_dates = [datetime.strptime(date_str, '%d %B %Y').date() for date_str in selected_date_strings]
        remove = request.POST.get('mark_on_site')
        changes_made, error_occurred = update_remote_days(employee, selected_dates, remove, request)

        if changes_made and not error_occurred:
            messages.success(request, "Les jours cochés ont été marqués comme sur place." if remove else "Votre demande à bien été envoyée aux managers.")
        employee.save()
        return redirect('setup')

    context = {
        'date_range': date_range,
        'selected_dates': employee.remote_days.values_list('date', flat=True),
        'next_week': next_week,
        'employee': employee,
        'week_days': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        'week_dates': date_range,
        'today': today,
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'setup.html', context)


@login_required
def calendar(request, next_week=0):
    query = request.GET.get('q', '')
    cleaned_query = clean_input(query) if query else ''
    show_remote = request.GET.get('show_remote', 'false') == 'true'
    today = date.today()

    if show_remote:
        employees = Employee.objects.filter(
            username__icontains=cleaned_query,
            is_superuser=False,
            remote_days__date=today
        )
    else:
        employees = Employee.objects.filter(
            username__icontains=cleaned_query,
            is_superuser=False
        )

    week_days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

    employees_with_remote_days = [
        {
            'employee': employee,
            'remote_days': [remote_request.remote_day.date for remote_request in
                            employee.remote_requests.filter(status='approved')],
            'remote_day_strs': [remote_request.remote_day.date.strftime('%Y-%m-%d') for remote_request in
                                employee.remote_requests.filter(status='approved')],
        } for employee in employees
    ]

    today = date.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=next_week)
    week_dates = get_date_range(week_start)
    fr_holidays = holidays.France(years=[d.year for d in week_dates])
    remote_employee_count = RemoteRequest.objects.filter(
        status='approved',
        remote_day__date=today,
    ).count()

    context = {
        'employees_with_remote_days': employees_with_remote_days,
        'week_days': week_days,
        'week_dates': week_dates,
        'today': today,
        'next_week': next_week,
        'pending_requests_count': pending_requests_count(request.user),
        'remote_employee_count': remote_employee_count,
        'holidays': [holiday for holiday in fr_holidays.keys() if holiday in week_dates],
    }

    return render(request, 'calendar.html', context)


@login_required
def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès!')
            return redirect('logout')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'account.html', context)


@login_required
def requests(request):
    if not request.user.is_manager:
        return redirect(reverse_lazy('calendar'))

    pending_requests = RemoteRequest.objects.filter(status='pending')

    context = {
        'pending_requests': pending_requests,
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'requests.html', context)


@login_required
def requests_status(request):
    status_filter = request.GET.get('status_filter', '')

    user_requests = RemoteRequest.objects.filter(employee=request.user).order_by('-remote_day__date')

    if status_filter:
        user_requests = user_requests.filter(status=status_filter)

    context = {
        'requests': user_requests,
        'status_filter': status_filter,
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'requests_status.html', context)


@login_required
@user_passes_test(lambda u: u.is_manager, login_url=reverse_lazy('calendar'))
@require_POST
def handle_request(request, request_id):
    remote_request = get_object_or_404(RemoteRequest, id=request_id)

    action = request.POST.get('action', '').lower()
    comment = request.POST.get('comment', '')
    cleaned_comment = clean_input(comment)
    remote_request.comment = cleaned_comment if cleaned_comment else ''

    allowed_actions = ['approve', 'reject']

    if action not in allowed_actions:
        return HttpResponseBadRequest("Action non autorisée")

    if action == 'approve':
        remote_request.status = 'approved'
    elif action == 'reject':
        remote_request.status = 'rejected'

    with transaction.atomic():
        remote_request.save()

    return redirect('requests')
