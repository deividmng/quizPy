from django.urls import path
from . import views


urlpatterns = [
    path('', views.hello),# el  '' esta vacio para que sea la primera vista 
    path('about/', views.about),# el  '' esta vacio para que sea la primera vista 
    path('hello/', views.hello),# el  '' esta vacio para que sea la primera vista 
    path('projects/', views.project_list, name='project_list'),
    
]