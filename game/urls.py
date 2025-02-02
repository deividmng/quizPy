from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path('python/', views.python_questions, name='python_questions'),
    path('randon/', views.randon_questions, name='randon_questions'),
    path("save_score/", views.save_score, name="save_score"),
    path('git/', views.git_questions, name='git_questions'),
    path('js/', views.js, name='js'),
    path('sql/', views.sql_questions, name='sql_questions'),  # 'sql/'
    path('question/<int:question_id>/', views.js, name='js_with_id'),
    path('reset_score/', views.reset_score, name='reset_score'),
    path('try_later/', views.try_later, name='try_later'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.singout, name='logout'),
    path('flashcard_form/', views.flashcard_form, name='flashcard_form'),
    path('flashcard_list/', views.flashcard_list, name='flashcard_list'),
    path('flashcard/<int:pk>/', views.flashcard_details, name='flashcard_details'),
    path('flashcard/update/<int:pk>/', views.update_flashcard, name='update_flashcard'),
    path('flashcard/delete/<int:pk>/', views.delete_flashcard, name='delete_flashcard'), 
]

