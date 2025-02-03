from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Project, Score
from .forms import FlashcardForm
from django.shortcuts import render, get_object_or_404, redirect






@login_required  # Asegura que el usuario esté autenticado
def save_score(request):
    if request.method == "POST":
        new_points = int(request.POST.get("points", 0))  # Recoge los puntos desde el formulario
        score, created = Score.objects.get_or_create(user=request.user)
        score.points += new_points  # Suma los puntos
        score.save()
    return redirect("leaderboard")  # Redirige a la tabla de clasificación

def leaderboard(request):
    # Obtiene todos los usuarios
    users = User.objects.all()

    # Crea una lista con usuarios y sus puntuaciones (si existen)
    leaderboard_data = []
    for user in users:
        score = Score.objects.filter(user=user).first()  # Obtiene la puntuación del usuario si existe
        leaderboard_data.append({
            "username": user.username,
            "points": score.points if score else 0  # Si no tiene puntuación, muestra 0
        })

    # Ordenar por puntos (descendente)
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)

    return render(request, "leaderboard.html", {"leaderboard_data": leaderboard_data})



@login_required
def flashcard_form(request):
    if request.method == 'POST':
        form = FlashcardForm(request.POST)
        if form.is_valid():
            flashcard = form.save(commit=False)  # No guarda aún
            flashcard.user = request.user  # Asocia el usuario a la flashcard
            flashcard.save()  # Guarda la flashcard con el usuario asociado
            return redirect('flashcard_list')  # Redirige a la lista de flashcards
    else:
        form = FlashcardForm()

    return render(request, 'flashcard_form.html', {'form': form})

@login_required
def flashcard_list(request):
    # Obtener todas las preguntas de la categoría 'Flashcard'
    flashcards = Project.objects.filter(user=request.user)
    # Índice de la pregunta actual
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Variables iniciales
    selected_answer = None
    is_correct = None

    # Contar las respuestas seleccionadas
    total_selected_answers = request.session.get('total_selected_answers', 0)

    if request.method == "POST":
        # Obtener el ID de la pregunta actual
        question_id = request.POST.get('question_id')
        flashcard = get_object_or_404(Project, id=question_id, category='Flashcard')

        # Respuesta seleccionada
        selected_answer = request.POST.get(f'answer_{flashcard.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_answers'] = total_selected_answers  # Guardar en la sesión

            # Validar si la respuesta es correcta
            if selected_answer == flashcard.correct_answer:
                request.session['flashcard_score'] = request.session.get('flashcard_score', 0) + 1
                is_correct = True
            else:
                # Registrar respuestas incorrectas en la sesión
                incorrect_answers = request.session.setdefault('flashcard_incorrect_answers', [])
                incorrect_answers.append({
                    'question': flashcard.question,
                    'your_answer': selected_answer,
                    'correct_answer': flashcard.correct_answer,
                })
                request.session.modified = True

        # Avanzar al siguiente índice sin importar si se seleccionó una respuesta o no
        current_question_index += 1

    # Si ya no hay más preguntas, mostrar un mensaje de que no hay más preguntas creadas
    if current_question_index >= len(flashcards):
        return render(request, 'no_more_questions.html', { 
            'message': "No more questions available.",
            'total_selected_answers': total_selected_answers
        })

    # Pregunta actual
    current_flashcard = flashcards[current_question_index]

    return render(request, 'flashcard_list.html', {
        'flashcard': current_flashcard,
        'current_question_index': current_question_index,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'total_selected_answers': total_selected_answers,
    })




def signup(request):
    if request.method == 'GET':
        # Pasamos un formulario vacío a la plantilla
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    else:
        # Proceso de creación de usuario y verificación de contraseña
        form = UserCreationForm(request.POST)  # Reconstruimos el formulario con los datos enviados
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request,user)
                return redirect('home')
                # return HttpResponse('User created successfully')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'User already exists'
                })
        else:
            return render(request, 'signup.html', {
                'form': form,
                'error': 'Passwords do not match'
            })
 


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, 
            username=request.POST['username'], 
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('home') 


def singout(request):
    logout(request)
    return redirect('home')


def home(request):
    # Obtener la lista de puntuaciones de todos los usuarios
    users = User.objects.all()
    leaderboard_data = []

    for user in users:
        score = Score.objects.filter(user=user).first()
        leaderboard_data.append({
            "username": user.username,
            "points": score.points if score else 0
        })

    # Ordenar la lista por puntos de forma descendente
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)

    # Pasar los datos del leaderboard a la plantilla
    return render(request, 'home.html', {
        'leaderboard_data': leaderboard_data
    })

def js(request):
    # Obtener todas las preguntas ordenadas por 'id'
    projects = Project.objects.filter(category='JavaScript').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para el mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Inicializar la sesión
    if 'score' not in request.session:
        request.session['score'] = 0
    if 'incorrect_answers' not in request.session:
        request.session['incorrect_answers'] = []
    if 'total_selected_js_answers' not in request.session:
        request.session['total_selected_js_answers'] = 0  # Inicializar el contador

    total_selected_answers = request.session['total_selected_js_answers']  # Obtener el contador actual

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_js_answers'] = total_selected_answers  # Guardar el contador en la sesión

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
            'incorrect_answers': request.session['incorrect_answers'],
            'total_selected_js_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    current_project = projects[current_question_index]

    # Definir el nivel dinámicamente
    level = "JavaScript Level 1"
    
    # Calcular las preguntas restantes
    remaining_questions = len(projects) - current_question_index - 1

    return render(request, 'project_list.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  # Pasar el mensaje de error al template
        'total_selected_js_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
        'level': level,  # Pasar el nivel al template
        'remaining_questions': remaining_questions,  # Pasar el número de preguntas restantes
    })


# Esta función restablecerá el puntaje y las respuestas incorrectas

def reset_score(request):
    # Reset score and incorrect answers, 
    request.session['score'] = 0
    request.session['incorrect_answers'] = []
    request.session['python_score'] = 0
    request.session['python_incorrect_answers'] = []
    request.session['git_score'] = 0
    request.session['git_incorrect_answers'] = []
    request.session['total_selected_git_answers'] = 0 # I added total_selected for git cause It did't refres the number 
    request.session['sql_score'] = 0
    request.session['sql_incorrect_answers'] = []
    request.session['flashcard_score'] = 0
    request.session['flashcard_incorrect_answers'] = []
    request.session['total_selected_answers'] = 0
    request.session['total_selected_python_answers'] = 0
    request.session['total_selected_sql_answers'] = 0
    request.session['total_selected_js_answers'] = 0
    request.session['total_selected_js_level_2_answers'] = 0
    request.session['total_selected_pythonL2_answers'] = 0
    request.session['pythonL2_score'] = 0
    request.session['pythonL2_incorrect_answers'] = []
    
    #Geting the URL to redirect after the game is done 
    next_url = request.POST.get('next_url', 'home')  #, 'home' in case it dont foun it it will send it at home 

    return redirect(next_url)

# try to connect with the resect_score 
#! it scras with the url that I save <why??
def try_later(request):
     # Reset score and incorrect answers, 
    # Reset score and incorrect answers, 
    request.session['score'] = 0
    request.session['incorrect_answers'] = []
    request.session['python_score'] = 0
    request.session['python_incorrect_answers'] = []
    request.session['git_score'] = 0
    request.session['git_incorrect_answers'] = []
    request.session['total_selected_git_answers'] = 0 # I added total_selected for git cause It did't refres the number 
    request.session['sql_score'] = 0
    request.session['sql_incorrect_answers'] = []
    request.session['flashcard_score'] = 0
    request.session['flashcard_incorrect_answers'] = []
    request.session['total_selected_answers'] = 0
    request.session['total_selected_python_answers'] = 0
    request.session['total_selected_sql_answers'] = 0
    request.session['total_selected_js_answers'] = 0
    request.session['total_selected_js_level_2_answers'] = 0
    return redirect('home')


def python_questions(request):
    python_projects = Project.objects.filter(category='Python').order_by('id')
    current_question_index = int(request.POST.get('current_question_index', 0))
    selected_answer = request.POST.get(f'answer_{request.POST.get("question_id")}', None)
    is_correct = None
    error_message = None

    # Contar las respuestas seleccionadas
    total_selected_answers = request.session.get('total_selected_python_answers', 0)

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_python_answers'] = total_selected_answers  # Guardar en la sesión

            # Validar si la respuesta es correcta
            if selected_answer == project.correct_answer:
                request.session['python_score'] = request.session.get('python_score', 0) + 1
                is_correct = True
            else:
                error_message = None
                request.session['python_incorrect_answers'].append({
                    'question': project.question,
                    'your_answer': selected_answer or "No answer selected",
                    'correct_answer': project.correct_answer
                })
                request.session.modified = True

            # Avanzar al siguiente índice
            current_question_index += 1
        else:
            # Si no se selecciona una respuesta, mostrar un mensaje de error y no avanzar
            error_message = "You must select an answer."

    # Si se han terminado las preguntas, redirigir a la página de resultados
    if current_question_index >= len(python_projects):
        return render(request, 'result.html', {
            'score': request.session.get('python_score', 0),
            'incorrect_answers': request.session.get('python_incorrect_answers', []),
            'total_selected_python_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    # Pregunta actual
    current_project = python_projects[current_question_index]
    
    remaining_questions = len(python_projects) - current_question_index - 1
    
    level = "Python Level 1"
        
    return render(request, 'python_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_python_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
        'level': level, 
        'remaining_questions': remaining_questions 
        
    })


def git_questions(request):
    git_projects = Project.objects.filter(category='Git').order_by('id')
    current_question_index = int(request.POST.get('current_question_index', 0))
    selected_answer = request.POST.get(f'answer_{request.POST.get("question_id")}', None)
    is_correct = None
    error_message = None

    # To avoid the error
    if 'git_incorrect_answers' not in request.session:
        request.session['git_incorrect_answers'] = []

    total_selected_answers = request.session.get('total_selected_git_answers', 0)

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            total_selected_answers += 1
            request.session['total_selected_git_answers'] = total_selected_answers

            if selected_answer == project.correct_answer:
                request.session['git_score'] = request.session.get('git_score', 0) + 1
                is_correct = True
            else:
                request.session['git_incorrect_answers'].append({
                    'question': project.question,
                    'your_answer': selected_answer or "No answer selected",
                    'correct_answer': project.correct_answer
                })
                request.session.modified = True

            current_question_index += 1
        else:
            error_message = "You must select an answer."

    if current_question_index >= len(git_projects):
        return render(request, 'result.html', {
            'score': request.session.get('git_score', 0),
            'incorrect_answers': request.session.get('git_incorrect_answers', []),
            'total_selected_git_answers': total_selected_answers
        })

    current_project = git_projects[current_question_index]
    
    remaining_questions = len(git_projects) - current_question_index - 1
   
    level = "SQL Level 1"

    return render(request, 'git_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_git_answers': total_selected_answers,
        'remaining_questions': remaining_questions,
        'level': level, 
    })


def sql_questions(request):
    sql_projects = Project.objects.filter(category='SQL').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para el mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Contar las respuestas seleccionadas
    total_selected_answers = request.session.get('total_selected_sql_answers', 0)

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_sql_answers'] = total_selected_answers  # Guardar en la sesión

            # Verificar si la respuesta es correcta
            is_correct = (selected_answer == project.correct_answer)
            if is_correct:
                request.session['sql_score'] = request.session.get('sql_score', 0) + 1
            else:
                # Respuesta incorrecta
                incorrect_answer = {
                    'question': project.question,
                    'your_answer': selected_answer,
                    'correct_answer': project.correct_answer,
                }
                incorrect_answers = request.session.setdefault('sql_incorrect_answers', [])
                incorrect_answers.append(incorrect_answer)
                request.session['sql_incorrect_answers'] = incorrect_answers
                request.session.modified = True

            # Avanzar al siguiente índice
            current_question_index += 1
        else:
            # Manejar el caso donde no se seleccionó una respuesta
            error_message = "You must select an answer."
            incorrect_answer = {
                'question': project.question,
                'your_answer': "No answer selected",
                'correct_answer': project.correct_answer,
            }
            incorrect_answers = request.session.setdefault('sql_incorrect_answers', [])
            incorrect_answers.append(incorrect_answer)
            request.session['sql_incorrect_answers'] = incorrect_answers
            request.session.modified = True
            # No avanzar al siguiente índice si no se selecciona respuesta

    # Verificar si el índice actual supera el total de preguntas
    if current_question_index >= len(sql_projects):
        return render(request, 'result.html', {
            'score': request.session.get('sql_score', 0),
            'incorrect_answers': request.session.get('sql_incorrect_answers', []),
            'total_selected_sql_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    current_project = sql_projects[current_question_index]
    
    remaining_questions = len(sql_projects) - current_question_index - 1
    
    level = "SQL Level 1"
    return render(request, 'sql_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_sql_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
        'remaining_questions': remaining_questions,
        'level': level, 
        
    })

#* update and delete 

@login_required
def flashcard_details(request, pk):
    flashcard = get_object_or_404(Project, pk=pk, category='Flashcard')  
    return render(request, 'flashcard_details.html', {'flashcard': flashcard})




@login_required
def update_flashcard(request, pk):
    flashcard = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        # Obtener valores del formulario
        flashcard.question = request.POST.get('question', flashcard.question)
        flashcard.choice_1 = request.POST.get('choice_1', flashcard.choice_1)
        flashcard.choice_2 = request.POST.get('choice_2', flashcard.choice_2)  # Si no está en el formulario, mantiene el valor anterior
        flashcard.choice_3 = request.POST.get('choice_3', flashcard.choice_3)
        flashcard.choice_4 = request.POST.get('choice_4', flashcard.choice_4)
        flashcard.correct_answer = request.POST.get('correct_answer', flashcard.correct_answer)

        # Guardar los cambios
        flashcard.save()
        
        # Redirigir a la lista de flashcards
        return redirect('flashcard_list')

    return render(request, 'flashcard_list', {'flashcard': flashcard})

@login_required
def delete_flashcard(request, pk):
    flashcard = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        flashcard.delete()
        return redirect('flashcard_list')  # Redirige a la lista de flashcards después de eliminar

    return render(request, 'delete_flashcard.html', {'flashcard': flashcard})


@login_required
def randon_questions(request):
    randon_questions_projects = Project.objects.filter(category='Randon').order_by('id')

    # Verifica si es una nueva partida (no se ha enviado POST aún)
    if request.method == "GET":
        request.session['randon_score'] = 0
        request.session['randon_incorrect_answers'] = []
        request.session['total_selected_randon_answers'] = 0

    current_question_index = int(request.POST.get('current_question_index', 0))
    selected_answer = request.POST.get(f'answer_{request.POST.get("question_id")}', None)
    is_correct = None
    error_message = None

    total_selected_answers = request.session.get('total_selected_randon_answers', 0)

    # Inicializar variables de sesión si no existen
    if 'randon_score' not in request.session:
        request.session['randon_score'] = 0
    if 'randon_incorrect_answers' not in request.session:
        request.session['randon_incorrect_answers'] = []

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            total_selected_answers += 1
            request.session['total_selected_randon_answers'] = total_selected_answers

            if selected_answer == project.correct_answer:
                request.session['randon_score'] = request.session.get('randon_score', 0) + 1
                is_correct = True
            else:
                request.session['randon_incorrect_answers'].append({
                    'question': project.question,
                    'your_answer': selected_answer or "No answer selected",
                    'correct_answer': project.correct_answer
                })
                request.session.modified = True

            current_question_index += 1
        else:
            error_message = "You must select an answer."

    # Calcular cuántas preguntas quedan
    remaining_questions = len(randon_questions_projects) - current_question_index

    # Si terminan las preguntas, guarda la puntuación en la base de datos
    if current_question_index >= len(randon_questions_projects):
        user_score = request.session.get('randon_score', 0)

        if request.user.is_authenticated:
            score, created = Score.objects.get_or_create(user=request.user)
            if not created:
                score.points += user_score
            else:
                score.points = user_score
            score.save()

        return redirect('leaderboard')

    # Pregunta actual
    current_project = randon_questions_projects[current_question_index]

    return render(request, 'randon_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_randon_answers': total_selected_answers,
        'remaining_questions': remaining_questions,  # Pasar las preguntas restantes
        'level': "Random Level"  # Pasar el nivel al template
    })


def js_level_2(request):
    # Obtener todas las preguntas ordenadas por 'id'
    projects = Project.objects.filter(category='JavaScriptL_2').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para el mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Inicializar la sesión
    if 'score' not in request.session:
        request.session['score'] = 0
    if 'incorrect_answers' not in request.session:
        request.session['incorrect_answers'] = []
    if 'total_selected_js_answers' not in request.session:
        request.session['total_selected_js_answers'] = 0  # Inicializar el contador

    total_selected_answers = request.session['total_selected_js_answers']  # Obtener el contador actual

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_js_answers'] = total_selected_answers  # Guardar el contador en la sesión

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
            'incorrect_answers': request.session['incorrect_answers'],
            'total_selected_js_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    current_project = projects[current_question_index]

    # Calcular las preguntas restantes
    remaining_questions = len(projects) - current_question_index - 1

    # Definir el nivel dinámicamente
    level = "JavaScript Level 2"

    return render(request, 'project_list.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  
        'total_selected_js_answers': total_selected_answers, 
        'level': level,  
        'remaining_questions': remaining_questions  
    })



def python_level_2(request):
    python_projects = Project.objects.filter(category='PythonL_2').order_by('id')
    current_question_index = int(request.POST.get('current_question_index', 0))
    selected_answer = request.POST.get(f'answer_{request.POST.get("question_id")}', None)
    is_correct = None
    error_message = None

    # Contar las respuestas seleccionadas
    total_selected_answers = request.session.get('total_selected_pythonL2_answers', 0)

    # Inicializar variables de sesión si no existen
    if 'pythonL2_score' not in request.session:
        request.session['pythonL2_score'] = 0
    if 'pythonL2_incorrect_answers' not in request.session:
        request.session['pythonL2_incorrect_answers'] = []

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_pythonL2_answers'] = total_selected_answers

            # Validar si la respuesta es correcta
            if selected_answer == project.correct_answer:
                request.session['pythonL2_score'] += 1
                is_correct = True
            else:
                error_message = None
                request.session['pythonL2_incorrect_answers'].append({
                    'question': project.question,
                    'your_answer': selected_answer or "No answer selected",
                    'correct_answer': project.correct_answer
                })
                request.session.modified = True

            # Avanzar al siguiente índice
            current_question_index += 1
        else:
            # Si no se selecciona una respuesta, mostrar un mensaje de error y no avanzar
            error_message = "You must select an answer."

    # Calcular cuántas preguntas quedan
    remaining_questions = len(python_projects) - current_question_index

    # Si se han terminado las preguntas, redirigir a la página de resultados
    if current_question_index >= len(python_projects):
        return render(request, 'result.html', {
            'score': request.session.get('pythonL2_score', 0),
            'incorrect_answers': request.session.get('pythonL2_incorrect_answers', []),
            'total_selected_pythonL2_answers': total_selected_answers
        })

    # Pregunta actual
    current_project = python_projects[current_question_index]

    level = "Python Level 2"
    return render(request, 'python_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_pythonL2_answers': total_selected_answers,
        'remaining_questions': remaining_questions,  # Pasar las preguntas restantes
        'level': level  # Pasar el nivel al template
    })

def sql_level_2(request):
    sql_projects = Project.objects.filter(category='SQL_level_2').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para mostrar un mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Inicializar la sesión si no existe
    if 'sql_score' not in request.session:
        request.session['sql_score'] = 0
    if 'sql_incorrect_answers' not in request.session:
        request.session['sql_incorrect_answers'] = []
    if 'total_selected_sql_answers' not in request.session:
        request.session['total_selected_sql_answers'] = 0  # Contador de respuestas seleccionadas

    total_selected_answers = request.session['total_selected_sql_answers']  # Obtener el contador actual

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_sql_answers'] = total_selected_answers  # Guardar en la sesión

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

            # Solo avanzar si se ha seleccionado una respuesta
            current_question_index += 1
        else:
            # No permitir avanzar si no selecciona una respuesta
            error_message = "You must select an answer."

    # Verificar si se completaron todas las preguntas
    if current_question_index >= len(sql_projects):
        return render(request, 'result.html', {
            'score': request.session['sql_score'],
            'incorrect_answers': request.session['sql_incorrect_answers'],
            'total_selected_sql_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    current_project = sql_projects[current_question_index]

    # Calcular preguntas restantes
    remaining_questions = len(sql_projects) - current_question_index - 1

    # Definir el nivel
    level = "SQL Level 2"

    return render(request, 'sql_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  
        'total_selected_sql_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
        'level': level,  
        'remaining_questions': remaining_questions  
    })


def git_level_2(request):
    git_projects = Project.objects.filter(category='Git_level_2').order_by('id')
    selected_answer = None
    is_correct = None
    error_message = None  # Variable para mostrar un mensaje de error
    current_question_index = int(request.POST.get('current_question_index', 0))

    # Inicializar la sesión si no existe
    if 'git_score' not in request.session:
        request.session['git_score'] = 0
    if 'git_incorrect_answers' not in request.session:
        request.session['git_incorrect_answers'] = []
    if 'total_selected_git_answers' not in request.session:
        request.session['total_selected_git_answers'] = 0  # Contador de respuestas seleccionadas

    total_selected_answers = request.session['total_selected_git_answers']  # Obtener el contador actual

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        project = Project.objects.get(id=question_id)
        selected_answer = request.POST.get(f'answer_{project.id}')

        if selected_answer:
            # Incrementar el contador de respuestas seleccionadas
            total_selected_answers += 1
            request.session['total_selected_git_answers'] = total_selected_answers  # Guardar en la sesión

            # Verificar si la respuesta es correcta
            is_correct = (selected_answer == project.correct_answer)
            if is_correct:
                request.session['git_score'] += 1
            else:
                # Respuesta incorrecta
                incorrect_answer = {
                    'question': project.question,
                    'your_answer': selected_answer,
                    'correct_answer': project.correct_answer,
                }
                incorrect_answers = request.session['git_incorrect_answers']
                incorrect_answers.append(incorrect_answer)
                request.session['git_incorrect_answers'] = incorrect_answers
                request.session.modified = True

            # Solo avanzar si se ha seleccionado una respuesta
            current_question_index += 1
        else:
            # No permitir avanzar si no selecciona una respuesta
            error_message = "You must select an answer."

    # Verificar si se completaron todas las preguntas
    if current_question_index >= len(git_projects):
        return render(request, 'result.html', {
            'score': request.session['git_score'],
            'incorrect_answers': request.session['git_incorrect_answers'],
            'total_selected_git_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    current_project = git_projects[current_question_index]

    # Calcular preguntas restantes
    remaining_questions = len(git_projects) - current_question_index - 1

    # Definir el nivel
    level = "Git Level 2"

    return render(request, 'git_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  
        'total_selected_git_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
        'level': level,  
        'remaining_questions': remaining_questions  
    })
