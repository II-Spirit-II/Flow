from django import forms
from django.contrib.auth.forms import UserCreationForm
from manager.models import Employee


class EmployeeForm(UserCreationForm):
    IS_MANAGER_CHOICES = (
        (False, 'Employé'),
        (True, 'Manager'),
    )

    is_manager = forms.ChoiceField(choices=IS_MANAGER_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Employee
        fields = ['username', 'email', 'password1', 'password2', 'is_manager']

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise forms.ValidationError("Le nom ne doit pas contenir d'espaces.")
        return username
