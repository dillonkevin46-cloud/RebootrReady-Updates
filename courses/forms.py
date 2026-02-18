from django import forms
from .models import Lecture, StudentNote, Category

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'description', 'category', 'word_document', 'order', 'is_unlocked', 'is_quiz_unlocked']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'is_unlocked': 'Unlock Module Content?',
            'is_quiz_unlocked': 'Unlock Quiz?'
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Human Resources, IT Security'}),
        }

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Select Excel File (.xlsx)",
        help_text="Format: Col A (Question), Col B (Explanation), Col C-F (Options), Col G (Correct Option #1-4)"
    )

class StudentNoteForm(forms.ModelForm):
    class Meta:
        model = StudentNote
        fields = ['annotated_html']

# --- NEW: Email Report Form ---
class EmailReportForm(forms.Form):
    manager_email = forms.EmailField(
        label="Manager's Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'manager@company.com', 'class': 'form-control'})
    )
    lecture = forms.ModelChoiceField(
        queryset=Lecture.objects.all().order_by('order'),
        label="Select Module to Report On",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message to include...'}),
        required=False,
        label="Additional Message"
    )