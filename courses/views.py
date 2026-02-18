from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils.text import slugify
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import mammoth
import openpyxl
import json

from .models import Lecture, Category, Question, Choice, QuizAttempt, StudentNote, Attendance
from .forms import LectureForm, ExcelUploadForm, StudentNoteForm, CategoryForm, EmailReportForm

# --- STUDENT VIEWS ---

@login_required
def lecture_list(request):
    if request.user.is_superuser:
        lectures = Lecture.objects.select_related('category', 'department').all().order_by('department', 'order')
    else:
        user_dept = request.user.department
        if user_dept:
            lectures = Lecture.objects.select_related('category', 'department').filter(department=user_dept).order_by('order')
        else:
            lectures = Lecture.objects.none()

    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        lectures = lectures.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )

    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        lectures = lectures.filter(category__slug=category_slug)
        current_category = Category.objects.filter(slug=category_slug).first()

    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.user.is_superuser:
         users = User.objects.filter(is_superuser=False, is_teacher=False).annotate(
             total_score=Sum('quizattempt__score', filter=Q(quizattempt__is_official_attempt=True))
         )
    else:
         if request.user.department:
            users = User.objects.filter(is_superuser=False, is_teacher=False, department=request.user.department).annotate(
                total_score=Sum('quizattempt__score', filter=Q(quizattempt__is_official_attempt=True))
            )
         else:
            users = User.objects.none()
    
    leaderboard = []
    for student in users:
        if student.total_score and student.total_score > 0:
            leaderboard.append(student)
            
    leaderboard.sort(key=lambda x: x.total_score, reverse=True)
    leaderboard = leaderboard[:10]

    context = {
        'lectures': lectures,
        'leaderboard': leaderboard,
        'categories': categories,
        'current_category': current_category,
        'search_query': query,
    }
    return render(request, 'courses/lecture_list.html', context)

@login_required
def lecture_detail(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    
    # Security Check
    if not request.user.is_superuser:
        if not request.user.department or lecture.department != request.user.department:
            messages.error(request, "You do not have access to this module.")
            return redirect('lecture_list')
    
    # --- TEACHER / ADMIN LOGIC ---
    is_preview_mode = request.user.is_teacher or request.user.is_superuser
    
    if is_preview_mode:
        # ALLOW SAVING NOTES for Teachers (New Fix)
        if request.method == "POST" and 'annotated_html_input' in request.POST:
            content = request.POST.get('annotated_html_input')
            note, created = StudentNote.objects.get_or_create(student=request.user, lecture=lecture)
            note.annotated_html = content
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Teacher notes saved!'})

        # Load existing notes if any
        content_html = ""
        note = StudentNote.objects.filter(student=request.user, lecture=lecture).first()
        if note and note.annotated_html:
            content_html = note.annotated_html
        elif lecture.word_document:
            try:
                with lecture.word_document.open() as f:
                    result = mammoth.convert_to_html(f)
                    content_html = result.value
            except Exception as e:
                content_html = f"<p class='text-danger'>Error loading document: {e}</p>"
                
        return render(request, 'courses/lecture_detail.html', {
            'lecture': lecture,
            'display_content': content_html,
            'has_attended': True, # Bypass blur
            'show_attendance_gate': False # Bypass modal
        })
    
    # --- STUDENT LOGIC ---
    if request.method == "POST" and 'attendance_agreement' in request.POST:
        Attendance.objects.get_or_create(student=request.user, lecture=lecture)
        messages.success(request, "Attendance Registered.")
        return redirect('lecture_detail', pk=pk)

    if request.method == "POST" and 'annotated_html_input' in request.POST:
        if Attendance.objects.filter(student=request.user, lecture=lecture).exists():
            content = request.POST.get('annotated_html_input')
            note, created = StudentNote.objects.get_or_create(student=request.user, lecture=lecture)
            note.annotated_html = content
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Notes saved!'})
        return JsonResponse({'status': 'error', 'message': 'Attendance required'}, status=403)

    has_attended = Attendance.objects.filter(student=request.user, lecture=lecture).exists()

    content_html = ""
    if has_attended:
        note, created = StudentNote.objects.get_or_create(student=request.user, lecture=lecture)
        if note.annotated_html:
            content_html = note.annotated_html
        else:
            if lecture.word_document:
                try:
                    with lecture.word_document.open() as f:
                        result = mammoth.convert_to_html(f)
                        content_html = result.value
                except Exception as e:
                    content_html = f"<p class='text-danger'>Error loading document: {e}</p>"

    return render(request, 'courses/lecture_detail.html', {
        'lecture': lecture,
        'display_content': content_html,
        'has_attended': has_attended,
        'show_attendance_gate': not has_attended
    })

@login_required
def save_notes(request, pk):
    # This view is legacy/fallback, but we update it just in case
    if request.method == "POST":
        lecture = get_object_or_404(Lecture, pk=pk)
        try:
            data = json.loads(request.body)
            html_content = data.get('html')
            note, created = StudentNote.objects.get_or_create(student=request.user, lecture=lecture)
            note.annotated_html = html_content
            note.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def take_quiz(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    
    if not request.user.is_superuser:
        if not request.user.department or lecture.department != request.user.department:
            messages.error(request, "Access Denied.")
            return redirect('lecture_list')

    if not lecture.can_take_quiz:
        messages.error(request, "This quiz is currently locked.")
        return redirect('lecture_list')

    questions = lecture.questions.all()
    
    if request.method == 'POST':
        score = 0
        total = questions.count()
        user_answers = {} 

        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    choice = Choice.objects.get(id=selected_choice_id)
                    user_answers[question.id] = choice.id
                    if choice.is_correct:
                        score += 1
                except Choice.DoesNotExist:
                    pass
        
        # --- "Don't Record" Logic for Teachers ---
        if request.user.is_teacher or request.user.is_superuser:
            # Create a Temporary (Unsaved) Attempt for display
            attempt = QuizAttempt(
                student=request.user,
                lecture=lecture,
                score=score,
                total_questions=total,
                is_official_attempt=False
            )
            
            # Manually build result data since we cannot query the DB for this attempt
            questions_data = []
            for q in questions:
                user_choice_id = user_answers.get(q.id)
                correct_choice = None
                user_choice = None
                
                for c in q.choices.all():
                    if c.is_correct:
                        correct_choice = c
                    if c.id == user_choice_id:
                        user_choice = c
                
                questions_data.append({
                    'question': q,
                    'user_choice': user_choice,
                    'correct_choice': correct_choice,
                    'is_correct': (user_choice.id == correct_choice.id) if user_choice and correct_choice else False
                })
            
            context = {
                'attempt': attempt,
                'results_data': questions_data
            }
            return render(request, 'courses/quiz_result.html', context)
            
        else:
            # STANDARD STUDENT LOGIC (Records to DB)
            existing_attempts = QuizAttempt.objects.filter(student=request.user, lecture=lecture).exists()
            is_official = not existing_attempts
            
            attempt = QuizAttempt.objects.create(
                student=request.user,
                lecture=lecture,
                score=score,
                total_questions=total,
                is_official_attempt=is_official
            )
            
            request.session[f'quiz_answers_{attempt.id}'] = user_answers
            return redirect('quiz_result', pk=attempt.id)

    return render(request, 'courses/quiz.html', {'lecture': lecture, 'questions': questions})

@login_required
def quiz_result(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk, student=request.user)
    
    user_answers_ids = request.session.get(f'quiz_answers_{attempt.id}', {})
    
    questions_data = []
    questions = attempt.lecture.questions.prefetch_related('choices').all()
    
    for q in questions:
        user_choice_id = user_answers_ids.get(str(q.id)) or user_answers_ids.get(q.id)
        
        correct_choice = None
        user_choice = None
        
        for c in q.choices.all():
            if c.is_correct:
                correct_choice = c
            if c.id == user_choice_id:
                user_choice = c
        
        questions_data.append({
            'question': q,
            'user_choice': user_choice,
            'correct_choice': correct_choice,
            'is_correct': (user_choice.id == correct_choice.id) if user_choice and correct_choice else False
        })

    context = {
        'attempt': attempt,
        'results_data': questions_data
    }
    return render(request, 'courses/quiz_result.html', context)

@login_required
def my_grades(request):
    attempts = QuizAttempt.objects.filter(student=request.user).order_by('-timestamp')
    return render(request, 'courses/my_grades.html', {'attempts': attempts})


# --- TEACHER VIEWS ---

def is_teacher_or_admin(user):
    return user.is_teacher or user.is_superuser

@user_passes_test(is_teacher_or_admin)
def teacher_dashboard(request):
    if request.user.is_superuser:
        lectures = Lecture.objects.select_related('category').all().order_by('department', 'order')
    else:
        lectures = Lecture.objects.select_related('category').filter(department=request.user.department).order_by('order')
        
    return render(request, 'courses/teacher_dashboard.html', {'lectures': lectures})

@user_passes_test(is_teacher_or_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(category.name)
            try:
                category.save()
                messages.success(request, f"Category '{category.name}' created!")
                return redirect('teacher_dashboard')
            except Exception:
                messages.error(request, "Error: Category with this name likely already exists.")
    else:
        form = CategoryForm()
    return render(request, 'courses/category_form.html', {'form': form, 'title': 'Create New Category'})

@user_passes_test(is_teacher_or_admin)
def lecture_create(request):
    if request.method == 'POST':
        form = LectureForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            if not request.user.is_superuser and not lecture.department:
                lecture.department = request.user.department
            lecture.save()
            messages.success(request, "Lecture created successfully!")
            return redirect('teacher_dashboard')
    else:
        form = LectureForm()
    return render(request, 'courses/lecture_form.html', {'form': form, 'title': 'Create Lecture'})

@user_passes_test(is_teacher_or_admin)
def lecture_edit(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    
    if not request.user.is_superuser:
        if lecture.department != request.user.department:
            messages.error(request, "Access Denied: You cannot edit lectures from another department.")
            return redirect('teacher_dashboard')
            
    if request.method == 'POST':
        form = LectureForm(request.POST, request.FILES, instance=lecture)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture updated successfully!")
            return redirect('teacher_dashboard')
    else:
        form = LectureForm(instance=lecture)
    return render(request, 'courses/lecture_form.html', {'form': form, 'title': 'Edit Lecture'})

@user_passes_test(is_teacher_or_admin)
def quiz_upload(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    
    if not request.user.is_superuser:
        if lecture.department != request.user.department:
            messages.error(request, "Access Denied.")
            return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                lecture.questions.all().delete()
                
                count = 0
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if not row or not row[0]: continue
                    q_text = str(row[0]).strip()
                    explanation = str(row[1]) if row[1] else ""
                    
                    question = Question.objects.create(lecture=lecture, text=q_text, explanation=explanation)
                    options = [row[2], row[3], row[4], row[5]]
                    
                    try:
                        correct_idx = int(row[6]) if row[6] else 1
                    except (ValueError, TypeError):
                        correct_idx = 1
                    
                    for i, opt_text in enumerate(options):
                        if opt_text:
                            Choice.objects.create(question=question, text=str(opt_text), is_correct=(i + 1 == correct_idx))
                    count += 1
                
                messages.success(request, f"Successfully uploaded {count} questions.")
                return redirect('teacher_dashboard')
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
    else:
        form = ExcelUploadForm()
    return render(request, 'courses/quiz_upload.html', {'lecture': lecture, 'form': form})

@user_passes_test(is_teacher_or_admin)
def teacher_results(request):
    query = request.GET.get('q')
    
    all_attempts = QuizAttempt.objects.select_related('student', 'lecture').order_by('-timestamp')
    
    if not request.user.is_superuser:
        if request.user.department:
            all_attempts = all_attempts.filter(lecture__department=request.user.department)
        else:
            all_attempts = all_attempts.none()
    
    if query:
        all_attempts = all_attempts.filter(
            Q(student__username__icontains=query) | 
            Q(lecture__title__icontains=query)
        )

    official_attempts = all_attempts.filter(is_official_attempt=True)
    retry_attempts = all_attempts.filter(is_official_attempt=False)

    context = {
        'official_attempts': official_attempts,
        'retry_attempts': retry_attempts,
        'search_query': query
    }
    return render(request, 'courses/teacher_results.html', context)

@user_passes_test(is_teacher_or_admin)
def teacher_attendance_report(request):
    records = Attendance.objects.select_related('student', 'lecture').all().order_by('-timestamp')
    
    if not request.user.is_superuser:
        if request.user.department:
            records = records.filter(lecture__department=request.user.department)
        else:
            records = records.none()
        
    return render(request, 'courses/teacher_attendance.html', {'records': records})

@user_passes_test(is_teacher_or_admin)
def email_report(request):
    if request.method == 'POST':
        form = EmailReportForm(request.POST)
        if form.is_valid():
            manager_email = form.cleaned_data['manager_email']
            lecture = form.cleaned_data['lecture']
            
            if not request.user.is_superuser:
                if lecture.department != request.user.department:
                     messages.error(request, "Access Denied.")
                     return redirect('teacher_dashboard')

            message_body = form.cleaned_data['message']

            attendance_records = Attendance.objects.filter(lecture=lecture).select_related('student')
            
            quiz_attempts = QuizAttempt.objects.filter(lecture=lecture).select_related('student').order_by('-score')
            student_best_scores = {}
            for attempt in quiz_attempts:
                if attempt.student.username not in student_best_scores:
                    student_best_scores[attempt.student.username] = attempt

            subject = f"Training Report: {lecture.title}"
            
            html_message = render_to_string('courses/email_report_template.html', {
                'lecture': lecture,
                'attendance_records': attendance_records,
                'student_best_scores': student_best_scores,
                'custom_message': message_body,
            })
            plain_message = strip_tags(html_message)

            try:
                send_mail(
                    subject,
                    plain_message,
                    'noreply@rebootready.com', 
                    [manager_email], 
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f"Report sent to {manager_email} successfully!")
                return redirect('teacher_dashboard')
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")

    else:
        form = EmailReportForm()
    
    return render(request, 'courses/email_report_form.html', {'form': form})