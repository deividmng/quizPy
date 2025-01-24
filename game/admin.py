from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'correct_answer')
    list_filter = ('category',)  # Añadir un filtro por categoría
    search_fields = ('question', 'correct_answer')  # Habilitar búsqueda por pregunta y respuesta correcta
    ordering = ('category',)  # Ordenar preguntas por categoría en el admin

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset
