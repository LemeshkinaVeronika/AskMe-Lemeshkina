from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



QUESTIONS = [
    {
        'title': f'Title {i}',
        'id': i,
        'text': f'Text for question # {i}',
        'tags': ['Primary', 'Secondary', 'Warning', 'Success', 'Danger', 'Info', 'Dark'][:i%7+1]
    } for i in range(30)
]

ANSWERS = [
    {
        'question_id': i % 5,  
        'id': i,
        'text': f'This is answer # {i} for question # {i % 5}',
        'likes': i * 3,
        'dislikes': i * 2,
        'is_correct': i % 2 == 0  
    } for i in range(30)  
]

# Create your views here.

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_num = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def tag_questions(request, tag_name):
    filtered_questions = [q for q in QUESTIONS if tag_name in q.get('tags', [])] 
    page = paginate(filtered_questions, request, per_page=5)
    return render(request, 'tag.html', context={'questions': page.object_list, 'tag': tag_name, 'page_obj': page})  

def question(request, question_id):
    question_answers = [a for a in ANSWERS if a['question_id'] == question_id]
    page = paginate(question_answers, request, per_page=3)
    return render(request, template_name="single_question.html", context={'question': QUESTIONS[question_id], 'answers': page.object_list, 'page_obj': page})

def index(request):
    page = paginate(QUESTIONS, request, per_page=5)
    return render(request, template_name="index.html", context={'questions': page.object_list, 'page_obj': page, 'is_authenticated': request.GET.get('auth') == '1'})

def hot(request):
    page = paginate(QUESTIONS, request, per_page=5)
    return render(request, template_name="hot.html", context={'questions': page.object_list, 'page_obj': page})

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