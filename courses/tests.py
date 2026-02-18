from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Lecture, Category, QuizAttempt
from .forms import LectureForm
from users.models import Department

class LectureFormTest(TestCase):
    def test_department_field_in_form(self):
        form = LectureForm()
        self.assertIn('department', form.fields)
        self.assertEqual(form.fields['department'].widget.attrs['class'], 'form-select')

class ViewOptimizationTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Technical')
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password', department=self.department)
        self.client = Client()
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')

    def test_lecture_list_queries(self):
        # Create 5 lectures linked to the user's department
        for i in range(5):
            Lecture.objects.create(title=f'L{i}', category=self.category, department=self.department, order=i)

        # Create 5 lectures in another department
        other_dept = Department.objects.create(name='Design')
        for i in range(5):
            Lecture.objects.create(title=f'Other{i}', category=self.category, department=other_dept, order=i)

        # Create some other users in same department to test leaderboard optimization
        User = get_user_model()
        for i in range(3):
            User.objects.create_user(username=f'user{i}', password='pw', department=self.department)

        # We expect a fixed number of queries regardless of number of users
        # The view queries:
        # 1. User/Session (auth)
        # 2. Lectures (select_related)
        # 3. Categories
        # 4. Users (leaderboard annotation)

        # We verify that the number of queries is reasonable.
        # Queries expected:
        # 1. Session
        # 2. User
        # 3. Lectures
        # 4. Categories
        # 5. Users (Leaderboard)
        # Maybe 1-2 more for auth/contenttypes
        # Queries executed:
        # 1. Session lookup
        # 2. User lookup
        # 3. User Department lookup (lazy load)
        # 4. Users Leaderboard (Annotated Query)
        # 5. Categories
        # 6. Lectures (select_related)
        with self.assertNumQueries(6):
            response = self.client.get(reverse('lecture_list'))
            self.assertEqual(response.status_code, 200)

    def test_leaderboard_optimization(self):
        # Create users and attempts
        User = get_user_model()
        dept = self.department

        # User with attempts
        u1 = User.objects.create_user(username='u1', password='pw', department=dept)
        l1 = Lecture.objects.create(title='L1', department=dept, order=1)

        QuizAttempt.objects.create(student=u1, lecture=l1, score=10, total_questions=10, is_official_attempt=True)
        QuizAttempt.objects.create(student=u1, lecture=l1, score=5, total_questions=10, is_official_attempt=False) # Should be ignored

        # Verify leaderboard logic in view context
        response = self.client.get(reverse('lecture_list'))
        leaderboard = response.context['leaderboard']

        # u1 should be in leaderboard with score 10
        found = False
        for entry in leaderboard:
            if entry.username == 'u1':
                self.assertEqual(entry.total_score, 10)
                found = True
        self.assertTrue(found)
