from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import Question, Tag, Answer, Profile
from .utils import paginate



# Create your views here.

def tag_questions(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=5)
    return render(request, 'tag.html', {'questions': page.object_list,'tag': tag, 'page_obj': page})

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question).order_by('-is_correct', '-created_at')
    page = paginate(answers, request, per_page=3)
    return render(request, 'single_question.html', {'question': question,'answers': page.object_list,'page_obj': page})

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'questions': page.object_list, 'page_obj': page})
def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=5)
    return render(request, 'hot.html', {'questions': page.object_list,'page_obj': page})

def ask(request):
    return render(request, 'ask.html')

def ask_submit(request):
    if request.method == 'POST':
        return redirect('index')  
    return redirect('ask')  

def answer_submit(request, question_id):
    if request.method == 'POST':
        return redirect('index')  
    return redirect('question')  

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def settings(request):
    return render(request, 'settings.html')

def login_submit(request):
    if request.method == 'POST':
        return redirect('index')
    return redirect('login')

def signup_submit(request):
    if request.method == 'POST':
        return redirect('index')
    return redirect('signup')

def settings_submit(request):
    if request.method == 'POST':
        return redirect('index')
    return redirect('settings')