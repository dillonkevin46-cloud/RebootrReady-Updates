from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        # Added 'department' to the fields list
        fields = ['username', 'email', 'first_name', 'last_name', 'is_teacher', 'department']
        widgets = {
            'is_teacher': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Styling for the dropdown
            'department': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {'is_teacher': 'Is this user a Lecturer?'}

class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # Added 'department' to the fields list
        fields = ['username', 'email', 'first_name', 'last_name', 'is_teacher', 'is_active', 'department']
        widgets = {
            'is_teacher': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Styling for the dropdown
            'department': forms.Select(attrs={'class': 'form-select'}),
        }