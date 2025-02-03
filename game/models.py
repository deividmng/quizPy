from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
class Project(models.Model):
    CATEGORY_CHOICES = [
        ('Flashcard', 'Flashcard'),
        ('JavaScript', 'JavaScript'),
        ('JavaScriptL_2', 'JavaScript_2'),
        ('Python', 'Python'),
        ('PythonL_2', 'PythonL_2'),
        ('SQL', 'SQL'),
        ('SQL_level_2', 'SQL_level_2'),
        ('Git', 'Git'),
        ('Git_level_2', 'Git_level_2'),
        ('Randon', 'Randon'),
        
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el modelo User
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
        choices = [self.choice_1, self.choice_2, self.choice_3, self.choice_4]
        if self.correct_answer not in choices:
            raise ValidationError(f"The correct_answer must match one of the choices: {choices}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.category}] {self.question}"


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    points = models.IntegerField(default=0)  # Puntos obtenidos por el usuario
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la puntuación

    def __str__(self):
        return f"{self.user.username} - {self.points} puntos"