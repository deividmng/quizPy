from django.http import HttpResponse ,JsonResponse
from django.shortcuts import render,redirect
from .models import Project


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
    # Reset score and incorrect answers, 
    request.session['score'] = 0
    request.session['incorrect_answers'] = []
    request.session['python_score'] = 0
    request.session['python_incorrect_answers'] = []
    request.session['sql_score'] = 0
    request.session['sql_incorrect_answers'] = []

    #Geting the URL to redirect after the game is done 
    next_url = request.POST.get('next_url', 'home')  #, 'home' in case it dont foun it it will send it at home 

    return redirect(next_url)


def try_later(request):
     # Reset score and incorrect answers, 
    request.session['score'] = 0
    request.session['incorrect_answers'] = []
    request.session['python_score'] = 0
    request.session['python_incorrect_answers'] = []
    request.session['sql_score'] = 0
    request.session['sql_incorrect_answers'] = []
    return redirect('home')


def python_questions(request):
    python_projects = Project.objects.filter(category='Python').order_by('id')
    current_question_index = int(request.POST.get('current_question_index', 0))
    selected_answer = request.POST.get(f'answer_{request.POST.get("question_id")}', None)
    is_correct = None
    error_message = None

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer == project.correct_answer:
            request.session['python_score'] += 1
            is_correct = True
        else:
            error_message = "You must select an answer." if not selected_answer else None
            request.session['python_incorrect_answers'].append({
                'question': project.question,
                'your_answer': selected_answer or "No answer selected",
                'correct_answer': project.correct_answer
            })
            request.session.modified = True

        current_question_index += 1

    # If the current question exceeds total, return the result page
    if current_question_index >= len(python_projects):
        return render(request, 'result.html', {
            'score': request.session.get('python_score', 0),
            'incorrect_answers': request.session.get('python_incorrect_answers', [])
        })

    # Proceed with the current project
    current_project = python_projects[current_question_index]
    return render(request, 'python_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
    })




def sql_questions(request):
    sql_projects = Project.objects.filter(category='SQL').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para el mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))


    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Verificar si la respuesta es correcta
            is_correct = (selected_answer == project.correct_answer)
            if is_correct:
                request.session['sql_score'] += 1
            else:
                # Respuesta incorrecta
                incorrect_answer = {
                    'question': project.question,
                    'your_answer': selected_answer,
                    'correct_answer': project.correct_answer,
                }
                incorrect_answers = request.session['sql_incorrect_answers']
                incorrect_answers.append(incorrect_answer)
                request.session['sql_incorrect_answers'] = incorrect_answers
                request.session.modified = True
        else:
            # Manejar el caso donde no se seleccionó una respuesta
            error_message = "You must select an answer."
            incorrect_answer = {
                'question': project.question,
                'your_answer': "No answer selected",
                'correct_answer': project.correct_answer,
            }
            incorrect_answers = request.session['sql_incorrect_answers']
            incorrect_answers.append(incorrect_answer)
            request.session['sql_incorrect_answers'] = incorrect_answers
            request.session.modified = True

        current_question_index += 1

    # Verificar si el índice actual supera el total de preguntas
    if current_question_index >= len(sql_projects):
        return render(request, 'result.html', {
            'score': request.session['sql_score'],
            'incorrect_answers': request.session['sql_incorrect_answers']
        })

    current_project = sql_projects[current_question_index]
    return render(request, 'sql_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  
    })


