from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import EmployeeForm
from django.contrib import messages


def add_form_errors_to_messages(request, form):
    for error in form.errors.as_data():
        messages.error(request, form.errors[error][0], extra_tags='danger')


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Identifiant ou mot de passe incorrect.')
        return super().form_invalid(form)

    def get_success_url(self):
        url = super().get_success_url()
        if self.request.user.is_superuser:
            url = '/admin/'
        return url


def register(request):
    if request.method == 'POST':
        employee_form = EmployeeForm(request.POST)
        if employee_form.is_valid():
            user = employee_form.save(commit=False)
            user.set_password(employee_form.cleaned_data["password1"])
            user.save()
            messages.success(request, 'Votre compte a été créé avec succès !')
            return redirect('login')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        employee_form = EmployeeForm()
    return render(request, 'register.html', {'employee_form': employee_form})
