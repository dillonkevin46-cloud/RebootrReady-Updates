from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Lecture(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='lectures')
    
    # NEW: Link Content to Department (using string reference to avoid circular imports)
    department = models.ForeignKey('users.Department', on_delete=models.SET_NULL, null=True, blank=True)
    
    word_document = models.FileField(upload_to='lectures/')
    order = models.PositiveIntegerField(default=0)
    
    # 1. Content Lock
    is_unlocked = models.BooleanField(default=False)
    
    # 2. Quiz Lock (Tick Box)
    is_quiz_unlocked = models.BooleanField(default=False, verbose_name="Unlock Quiz?")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"

    @property
    def can_take_quiz(self):
        return self.is_unlocked and self.is_quiz_unlocked

class Question(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_official_attempt = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.lecture.title}"

class StudentNote(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    annotated_html = models.TextField(blank=True, default="")
    
    class Meta:
        unique_together = ('student', 'lecture')

class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'lecture')