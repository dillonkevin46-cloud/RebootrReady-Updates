from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from .models import CustomUser, Profile
from .forms import UserUpdateForm, ProfileUpdateForm, CustomUserCreationForm, CustomUserEditForm

@login_required
def profile(request):
    # --- SAFETY FIX: Create Profile if missing (Fixes 500 Error) ---
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    # ---------------------------------------------------------------

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

# --- ADMIN VIEWS ---
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def manage_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {'users': users})

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New user created successfully!')
            return redirect('manage_users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Create New User'})

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user_obj.username} updated!')
            return redirect('manage_users')
    else:
        form = CustomUserEditForm(instance=user_obj)
    return render(request, 'users/user_form.html', {'form': form, 'title': f'Edit User: {user_obj.username}'})

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('manage_users')
    return render(request, 'users/user_confirm_delete.html', {'user_obj': user_obj})

@user_passes_test(is_admin)
def admin_password_reset(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for {user_obj.username} has been reset.')
            return redirect('manage_users')
    else:
        form = SetPasswordForm(user_obj)
    return render(request, 'users/user_form.html', {'form': form, 'title': f'Reset Password for {user_obj.username}'})