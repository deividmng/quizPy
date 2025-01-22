from django.urls import path
from . import views


urlpatterns = [
    path('', views.hello),# el  '' esta vacio para que sea la primera vista 
    path('about/', views.about),# el  '' esta vacio para que sea la primera vista 
]