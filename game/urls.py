from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('python/', views.python_questions, name='python_questions'),
    path('js/', views.js, name='js'),
    path('sql/', views.sql_questions, name='sql_questions'),  # 'sql/'
    path('question/<int:question_id>/', views.js, name='js_with_id'),
    path('reset_score/', views.reset_score, name='reset_score'),
    path('try_later/', views.try_later, name='try_later'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signin/', views.signin, name='signin'),
    path('flashcard_form/', views.flashcard_form, name='flashcard_form'),
    path('flashcard_list/', views.flashcard_list, name='flashcard_list'), 
]
