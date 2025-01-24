from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('python/', views.python),# el  '' esta vacio para que sea la primera vista 
    path('js/', views.js, name='js'),
    path('question/<int:question_id>/', views.js, name='js_with_id'), 
    path('reset_score/', views.reset_score, name='reset_score'), 
    # path('projects/', views.project_list, name='project_list'),
    
]