from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    
    # --- Password Reset Flow ---
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),

    # --- Admin URLs ---
    path('manage/', views.manage_users, name='manage_users'),
    path('manage/create/', views.create_user, name='create_user'),
    path('manage/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage/reset-password/<int:user_id>/', views.admin_password_reset, name='admin_password_reset'),
]