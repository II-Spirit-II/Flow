from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .models import Employee, RemoteRequest
from .models import RemoteDay
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import date, datetime, timedelta
from django.core.validators import validate_unicode_slug
from django.core.exceptions import ValidationError
import holidays
import locale
import smtplib

# Set the locale to French
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


# This function is used to sanitize the input string by checking if it's a valid unicode slug.
# If the input is not a valid slug, it returns an empty string.
def clean_input(input_str):
    try:
        validate_unicode_slug(input_str)
    except ValidationError:
        return ''
    return input_str

def send_status_update_email(self, remote_requests):
    approved_requests = [r for r in remote_requests if r.status == 'approved']
    rejected_requests = [r for r in remote_requests if r.status == 'rejected']

    context = {
        'employee': self,
        'approved_dates': [r.remote_day.date.strftime("%d %B %Y") for r in approved_requests],
        'rejected_dates': [r.remote_day.date.strftime("%d %B %Y") for r in rejected_requests],
    }

    email_body = render_to_string('requests_status_email.html', context)

    try:
        send_mail(
            'Mise à jour du statut de vos demandes de télétravail',
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
            html_message=email_body,
        )
    except smtplib.SMTPRecipientsRefused:
        pass  # Ignore l'erreur si l'e-mail ne peut pas être envoyé.

# This function returns the number of pending remote work requests if the user is a manager.

def pending_requests_count(user):
    if user.is_manager:
        return RemoteRequest.objects.filter(status='pending', employee__center=user.center).count()
    return 0


# This function returns a list of dates for the 5-day work week starting from the provided date.

def get_date_range(week_start):
    return [week_start + timedelta(days=i) for i in range(5)]


# This function updates the list of remote work days for a given employee.
# It validates the selected dates and returns error messages if the dates are invalid (e.g., past dates, holidays).
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
        return False, True

    remote_days_to_update = RemoteDay.objects.filter(date__in=valid_dates)
    employee.remote_days.remove(*remote_days_to_update)
    RemoteRequest.objects.filter(employee=employee, remote_day__in=remote_days_to_update).delete()

    new_requests = []  # Liste pour stocker les nouvelles demandes

    if not remove:
        for selected_date in valid_dates:
            remote_day, created = RemoteDay.objects.get_or_create(date=selected_date)
            employee.remote_days.add(remote_day)
            comment = request.POST.get('comment', '')
            remote_request, created = RemoteRequest.objects.get_or_create(employee=employee, remote_day=remote_day,
                                                                          status='pending', comment=comment)
            if created:  # Si une nouvelle demande de télétravail a été créée
                new_requests.append(remote_request)  # Ajouter à la liste des nouvelles demandes

    # Skip sending emails and notifications if the request is made by a manager
    if not request.user.is_manager and new_requests:
        # Filter managers by the same center as the employee
        managers = Employee.objects.filter(is_manager=True, center=employee.center)

        for manager in managers:
            context = {
                'employee': employee,
                'dates': [r.remote_day.date.strftime("%d %B %Y") for r in new_requests],
                'comments': [r.comment for r in new_requests],
            }

            email_body = render_to_string('requests_email.html', context)

            send_mail(
                'Nouvelles demandes de télétravail',
                '',
                settings.EMAIL_HOST_USER,
                [manager.email],
                fail_silently=False,
                html_message=email_body,
            )

    return bool(valid_dates), False


# This view handles the setup of the user's work week. It allows the user to select which days they want to work.
@login_required
def setup(request, next_week=0):
    employee = request.user

    if employee.is_superuser:
        return redirect(reverse_lazy('admin:index'))

    today = date.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=next_week)
    date_range = get_date_range(week_start)
    fr_holidays = holidays.France(years=[today.year, today.year + 1])
    formatted_holidays = [h.strftime('%Y-%m-%d') for h in fr_holidays]

    if request.method == 'POST':
        selected_date_strings = request.POST.getlist('remote_days')
        selected_dates = [datetime.strptime(date_str, '%d %B %Y').date() for date_str in selected_date_strings]
        remove = request.POST.get('mark_on_site')
        try:
            changes_made, error_occurred = update_remote_days(employee, selected_dates, remove, request)
        except smtplib.SMTPRecipientsRefused:
            changes_made, error_occurred = True, True  # changes_made set to True

        if changes_made:
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
        'holidays': formatted_holidays,
    }

    return render(request, 'setup.html', context)


# This view displays a calendar of employees' remote work days.
# It can filter the employees based on a query string and whether they have an approved remote day for today.
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
            center=request.user.center,  # Filter by center
            remote_days__date=today,
            remote_requests__status="approved",
            remote_requests__remote_day__date=today
        )
    else:
        employees = Employee.objects.filter(
            username__icontains=cleaned_query,
            is_superuser=False,
            center=request.user.center  # Filter by center
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
    
    # Update the remote_employee_count to filter by the user's center
    remote_employee_count = RemoteRequest.objects.filter(
        status='approved',
        remote_day__date=today,
        employee__center=request.user.center  # Filter by center
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


# This view allows the user to change their account password.
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


# This view displays a list of all pending remote work requests. It is only accessible to managers.
@login_required
def requests(request):
    if not request.user.is_manager:
        return redirect(reverse_lazy('calendar'))

    # Filtrer les demandes par centre et statut
    pending_requests_list = RemoteRequest.objects.filter(
        status='pending',
        employee__center=request.user.center  # Vérification du centre
    ).order_by('id')

    # Pagination
    paginator = Paginator(pending_requests_list, 5)  # 5 demandes par page
    page_number = request.GET.get('page')
    pending_requests = paginator.get_page(page_number)

    context = {
        'pending_requests': pending_requests,  # Variable utilisée dans le template
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'requests.html', context)


# This view displays the status of the user's remote work requests.
@login_required
def requests_status(request):
    status_filter = request.GET.get('status_filter', '')

    user_requests = RemoteRequest.objects.filter(employee=request.user).order_by('-remote_day__date')

    if status_filter:
        user_requests = user_requests.filter(status=status_filter)

    paginator = Paginator(user_requests, 5)  # Show 5 requests per page.

    page_number = request.GET.get('page')
    user_requests = paginator.get_page(page_number)

    context = {
        'requests': user_requests,
        'status_filter': status_filter,
        'pending_requests_count': pending_requests_count(request.user),
    }

    return render(request, 'requests_status.html', context)


# This view allows managers to approve or reject remote work requests.
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

    # Récupérer l'employé concerné par la demande
    employee = remote_request.employee

    # Préparer le corps du mail
    context = {
        'employee': employee,
        'date': remote_request.remote_day.date.strftime("%d %B %Y"),
        'status': remote_request.status,  # Ajouter le statut à l'objet contexte
        'comment': remote_request.comment,  # Utiliser le commentaire de la demande
    }

    email_body = render_to_string('requests_status_email.html', context)

    # Envoyer un email à l'employé concerné
    with transaction.atomic():
        remote_request.save()

    try:
        # Envoyer un email à l'employé concerné
        send_mail(
            'Mise à jour du statut de vos demandes de télétravail',
            '',
            settings.EMAIL_HOST_USER,
            [employee.email],
            fail_silently=False,
            html_message=email_body,
        )
    except smtplib.SMTPRecipientsRefused:
        pass  # Ignorer l'erreur d'envoi de courrier électronique

    return redirect('requests')

@login_required
@user_passes_test(lambda u: u.is_manager)
def manager_setup(request, employee_uuid, next_week=0):
    employee = get_object_or_404(Employee, uuid=employee_uuid)

    today = date.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=next_week)
    date_range = get_date_range(week_start)
    fr_holidays = holidays.France(years=[today.year, today.year + 1])
    formatted_holidays = [h.strftime('%Y-%m-%d') for h in fr_holidays]

    if request.method == 'POST':
        selected_date_strings = request.POST.getlist('remote_days')
        selected_dates = [datetime.strptime(date_str, '%d %B %Y').date() for date_str in selected_date_strings]
        remove = request.POST.get('mark_on_site')
        update_remote_days(employee, selected_dates, remove, request)
        employee.save()
        return redirect('calendar')

    context = {
        'date_range': date_range,
        'selected_dates': employee.remote_days.values_list('date', flat=True),
        'next_week': next_week,
        'employee': employee,
        'week_days': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        'week_dates': date_range,
        'today': today,
        'pending_requests_count': pending_requests_count(request.user),
        'holidays': formatted_holidays,
    }

    return render(request, 'setup.html', context)