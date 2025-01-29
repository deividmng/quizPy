from django.http import HttpResponse ,JsonResponse
from django.shortcuts import render,redirect
from .models import Project
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth import login ,logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import FlashcardForm
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


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
    error_message = None

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

            # Avanzar al siguiente índice
            current_question_index += 1
        else:
            # Generar un mensaje de error si no se selecciona ninguna respuesta
            error_message = "You must select an answer."

    # Si se han terminado las preguntas, redirigir a la página de resultados
    if current_question_index >= len(flashcards):
        return render(request, 'result.html', {
            'score': request.session.get('flashcard_score', 0),
            'incorrect_answers': request.session.get('flashcard_incorrect_answers', []),
            'total_selected_answers': total_selected_answers  # Pasar el total de respuestas seleccionadas
        })

    # Pregunta actual
    current_flashcard = flashcards[current_question_index]

    return render(request, 'flashcard_list.html', {
        'flashcard': current_flashcard,
        'current_question_index': current_question_index,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'error_message': error_message,
        'total_selected_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
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
    return render(request, 'home.html')

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
    return render(request, 'project_list.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,  # Pasar el mensaje de error al template
        'total_selected_js_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
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
    request.session['flashcard_score'] = 0
    request.session['flashcard_incorrect_answers'] = []
    request.session['total_selected_answers'] = 0
    request.session['total_selected_python_answers'] = 0
    request.session['total_selected_sql_answers'] = 0
    request.session['total_selected_js_answers'] = 0
    
    #Geting the URL to redirect after the game is done 
    next_url = request.POST.get('next_url', 'home')  #, 'home' in case it dont foun it it will send it at home 

    return redirect(next_url)

# try to connect with the resect_score 
#! it scras with the url that I save <why??
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

    return render(request, 'python_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_python_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
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
    return render(request, 'sql_questions.html', {
        'project': current_project,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'current_question_index': current_question_index,
        'error_message': error_message,
        'total_selected_sql_answers': total_selected_answers,  # Pasar el total de respuestas seleccionadas
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
        # getting the value from the form
        flashcard.question = request.POST['question']
        flashcard.choice_1 = request.POST['choice_1']
        flashcard.choice_2 = request.POST['choice_2']
        flashcard.choice_3 = request.POST['choice_3']
        flashcard.choice_4 = request.POST['choice_4']
        flashcard.correct_answer = request.POST['correct_answer']
        
        # Saving the new date 
        flashcard.save()
        
        # Redirigir a la vista de detalles de la flashcard
        return redirect('flashcard_list',)

    return render(request, 'flashcard_list', {'flashcard': flashcard})

@login_required
def delete_flashcard(request, pk):
    flashcard = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        flashcard.delete()
        return redirect('flashcard_list')  # Redirige a la lista de flashcards después de eliminar

    return render(request, 'delete_flashcard.html', {'flashcard': flashcard})