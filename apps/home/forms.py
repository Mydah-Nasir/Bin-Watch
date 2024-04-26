from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddUserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    qalamId = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Qalam Id",
                "class": "form-control"
            }
        ))
    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    department = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Department",
                "class": "form-control"
            }
        ))
    batch = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Batch",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))
    is_admin_choices = (
        (False, "User"),
        (True, "Admin")
    )
    is_admin = forms.ChoiceField(
        choices=is_admin_choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "User",
            }
        )
    )

class EditProfileForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
    ))
    qalamId = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Qalam Id",
                "class": "form-control",
            }
        ))
    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    department = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Department",
                "class": "form-control"
            }
        ))
    batch = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Batch",
                "class": "form-control"
            }
        ))

class EditUserForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
    ))
    qalamId = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Qalam Id",
                "class": "form-control",
            }
        ))
    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    department = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Department",
                "class": "form-control"
            }
        ))
    batch = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Batch",
                "class": "form-control"
            }
        ))
    is_admin_choices = (
        (False, "User"),
        (True, "Admin")
    )
    is_admin = forms.ChoiceField(
        choices=is_admin_choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "User",
            }
        )
    )

class ReportUserForm(forms.Form):
    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    department = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Department",
                "class": "form-control"
            }
        ))
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))

class VerifyReportForm(forms.Form):
    is_valid_choices = (
        (False, "Not Verified"),
        (True, "Verified")
    )
    is_valid = forms.ChoiceField(
        choices=is_valid_choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Status",
            }
        )
    )
