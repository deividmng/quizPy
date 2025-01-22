from django.urls import path
from . import views


urlpatterns = [
    path('', views.hello),# el  '' esta vacio para que sea la primera vista 
    path('about/', views.about),# el  '' esta vacio para que sea la primera vista 
    path('hello/', views.hello, name='hello'),
    path('question/<int:question_id>/', views.hello, name='hello_with_id'), 
    path('reset_score/', views.reset_score, name='reset_score'), 
    # path('projects/', views.project_list, name='project_list'),
    
]