from django.contrib import admin
from .models import Lecture, Category, Question, Choice, QuizAttempt, StudentNote, Attendance

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    # Updated List Display
    list_display = ('title', 'category', 'order', 'is_unlocked', 'is_quiz_unlocked')
    list_editable = ('order', 'is_unlocked', 'is_quiz_unlocked')
    list_filter = ('category', 'is_unlocked', 'is_quiz_unlocked')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'score', 'timestamp', 'is_official_attempt')
    list_filter = ('lecture', 'is_official_attempt')

@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'timestamp')
    list_filter = ('lecture', 'timestamp')