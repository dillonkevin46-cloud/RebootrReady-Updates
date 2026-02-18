from django.urls import path
from . import views

urlpatterns = [
    # Student Views
    path('', views.lecture_list, name='lecture_list'),
    path('my-grades/', views.my_grades, name='my_grades'),
    path('<int:pk>/', views.lecture_detail, name='lecture_detail'),
    path('<int:pk>/quiz/', views.take_quiz, name='take_quiz'),
    path('<int:pk>/quiz/result/', views.quiz_result, name='quiz_result'),
    path('<int:pk>/save_notes/', views.save_notes, name='save_notes'),
    
    # Teacher Views
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/results/', views.teacher_results, name='teacher_quiz_results'),
    path('teacher/attendance/', views.teacher_attendance_report, name='teacher_attendance_report'),
    
    # NEW: Email Report
    path('teacher/email-report/', views.email_report, name='email_report'),

    path('teacher/add/', views.lecture_create, name='lecture_create'),
    path('teacher/category/add/', views.category_create, name='category_create'),
    path('teacher/edit/<int:pk>/', views.lecture_edit, name='lecture_edit'),
    path('teacher/upload-quiz/<int:pk>/', views.quiz_upload, name='quiz_upload'),
]