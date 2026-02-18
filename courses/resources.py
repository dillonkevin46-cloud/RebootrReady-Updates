from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Question, Choice, Lecture

class QuestionResource(resources.ModelResource):
    # 1. Allow mapping by Lecture Title instead of ID number
    lecture = fields.Field(
        column_name='lecture_title',
        attribute='lecture',
        widget=ForeignKeyWidget(Lecture, field='title')
    )

    class Meta:
        model = Question
        # These are the columns Django will look for in the Questions table
        fields = ('lecture', 'text', 'explanation')
        export_order = ('lecture', 'text', 'explanation')
        # We don't import ID, so every row becomes a new question
        exclude = ('id',)

    # --- THE FIX IS HERE ---
    # We added **kwargs to accept the unexpected arguments like 'form'
    def __init__(self, **kwargs):
        super().__init__()
        self.current_row = None

    def before_import_row(self, row, **kwargs):
        # Capture the row data before processing starts
        self.current_row = row

    def after_save_instance(self, instance, using_transactions, dry_run):
        """
        After the Question is saved, we look at the Excel row again
        and create the Choice options attached to this Question.
        """
        if dry_run or not self.current_row:
            return

        # 1. Clear existing choices (to prevent duplicates if re-uploading logic changes)
        instance.choices.all().delete()

        # 2. Get the Correct Answer Number (e.g., 1, 2, or 3)
        # We assume the user types '1', '2', etc. in the Excel file
        try:
            # We treat everything as string first, then int, to be safe
            val = str(self.current_row.get('correct_number')).strip()
            # If it's a float like 1.0, convert to float then int
            correct_index = int(float(val)) if val else 0
        except (ValueError, TypeError):
            correct_index = 0 

        # 3. Loop through 4 potential options columns: 'option_1', 'option_2', etc.
        for i in range(1, 5):
            key = f'option_{i}'
            choice_text = self.current_row.get(key)
            
            if choice_text:
                # Check if this specific option is the correct one
                is_right = (i == correct_index)
                
                # Create the Choice in the database
                Choice.objects.create(
                    question=instance,
                    text=choice_text,
                    is_correct=is_right
                )