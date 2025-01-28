# forms.py
from django import forms
from .models import Project

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['question', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_answer', 'category']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your question here'}),
            'choice_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'choice_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 2'}),
            'choice_3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 3'}),
            'choice_4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 4'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correct Answer'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
