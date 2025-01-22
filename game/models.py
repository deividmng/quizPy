from django.db import models

# Create your models here.


    
from django.db import models
from django.core.exceptions import ValidationError

class Project(models.Model):
    question = models.TextField(null=False)
    choice_1 = models.TextField(blank=True, null=True)
    choice_2 = models.TextField(blank=True, null=True)
    choice_3 = models.TextField(blank=True, null=True)
    choice_4 = models.TextField(blank=True, null=True)
    correct_answer = models.TextField()

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
        return self.question
