from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_answer')
    list_filter = ('correct_answer',)
    search_fields = ('question', 'choice_1', 'choice_2', 'choice_3', 'choice_4')
    ordering = ('question',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

admin.site.register(Project, ProjectAdmin)

