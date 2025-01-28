from django.db import models
from django.core.exceptions import ValidationError

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('JavaScript', 'JavaScript'),
        ('Python', 'Python'),
        ('SQL', 'SQL'),  # Nueva categoría para preguntas de SQL
        ('Flashcard', 'Flashcard'),  # Nueva categoría
    ]

    question = models.TextField(null=False)
    choice_1 = models.TextField(blank=True, null=True)
    choice_2 = models.TextField(blank=True, null=True)
    choice_3 = models.TextField(blank=True, null=True)
    choice_4 = models.TextField(blank=True, null=True)
    correct_answer = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='JavaScript',
        help_text="Select the category for this question."
    )

    def clean(self):
        """
        Ensure correct_answer is one of the choices.
        """
        choices = [self.choice_1, self.choice_2, self.choice_3, self.choice_4]
        if self.correct_answer not in choices:
            raise ValidationError(
                f"The correct_answer must match one of the choices: {choices}"
            )

    def save(self, *args, **kwargs):
        # Call the clean method before saving the object.
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.category}] {self.question}"
