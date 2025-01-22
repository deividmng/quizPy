# from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .models import Project


# Create your views here.
def hello(request):
 return HttpResponse('<h1>david</h1>')


def about(request):
    return HttpResponse('<h1>about</h1>')

from django.shortcuts import render
from .models import Project

def project_list(request):
    # Recupera todos los registros de la tabla Project
    projects = Project.objects.all()
    selected_answer = None
    is_correct = None

    if request.method == "POST":
        question_id = request.POST.get('question_id')  # ID de la pregunta seleccionada
        selected_answer = request.POST.get('answer')  # Respuesta seleccionada
        project = Project.objects.get(id=question_id)  # Obtiene la pregunta de la BD

        # Verifica si la respuesta seleccionada es correcta
        is_correct = (selected_answer == project.correct_answer)

    return render(request, 'project_list.html', {
        'projects': projects,
        'selected_answer': selected_answer,
        'is_correct': is_correct
    })
