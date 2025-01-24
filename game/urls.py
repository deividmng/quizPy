from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('python/', views.python_questions, name='python_questions'),
    path('js/', views.js, name='js'),
    path('sql/', views.sql_questions, name='sql_questions'),  # Cambiado a 'sql/'
    path('question/<int:question_id>/', views.js, name='js_with_id'),
    path('reset_score/', views.reset_score, name='reset_score'),
]
