# from django.shortcuts import render
from django.http import HttpResponse ,JsonResponse
from django.shortcuts import render,redirect
from .models import Project
import random

def home(request):
    return render(request, 'home.html')


def js(request):
    # Obtener todas las preguntas ordenadas por 'id'
    projects = Project.objects.all().order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para el mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Inicializar la sesión
    if 'score' not in request.session:
        request.session['score'] = 0
    if 'incorrect_answers' not in request.session:
        request.session['incorrect_answers'] = []

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Verificar si la respuesta es correcta
            is_correct = (selected_answer == project.correct_answer)
            if is_correct:
                request.session['score'] += 1
            else:
                # Respuesta incorrecta
                incorrect_answer = {
                    'question': project.question,
                    'your_answer': selected_answer,
                    'correct_answer': project.correct_answer,
                }
                incorrect_answers = request.session['incorrect_answers']
                incorrect_answers.append(incorrect_answer)
                request.session['incorrect_answers'] = incorrect_answers
                request.session.modified = True
        else:
            # Manejar el caso donde no se seleccionó una respuesta
            error_message = "You must select an answer."
            incorrect_answer = {
                'question': project.question,
                'your_answer': "No answer selected",
                'correct_answer': project.correct_answer,
            }
            incorrect_answers = request.session['incorrect_answers']
            incorrect_answers.append(incorrect_answer)
            request.session['incorrect_answers'] = incorrect_answers
            request.session.modified = True

        current_question_index += 1

    # Verificar si el índice actual supera el total de preguntas
    if current_question_index >= len(projects):
        return render(request, 'result.html', {
            'score': request.session['score'],
            'incorrect_answers': request.session['incorrect_answers']
        })

    current_project = projects[current_question_index]
    return render(request, 'project_list.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  # Pasar el mensaje de error al template
    })

# Esta función restablecerá el puntaje y las respuestas incorrectas
def reset_score(request):
    # Aquí restablecemos el puntaje y las respuestas incorrectas a sus valores iniciales.
    request.session['score'] = 0
    request.session['incorrect_answers'] = []

    return redirect('home')  # Redirigimos a la página principal del juego (home)


def python(request):
    return HttpResponse('<h1>python</h1>')

