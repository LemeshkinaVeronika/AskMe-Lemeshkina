from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import Question, Tag, Answer, Profile, QuestionLike
from .utils import paginate, handle_question_vote, handle_answer_vote, handle_correct_answer, add_vote_context
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import AskQuestionForm, AnswerForm, LoginForm, SignUpForm, ProfileEditForm


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
    user_vote = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            vote = QuestionLike.objects.filter(question=question, user=profile).first()
            if vote:
                user_vote = vote.is_like
        except Profile.DoesNotExist:
            pass
    return render(request, 'single_question.html', {'question': question,'answers': page.object_list,'page_obj': page, 'user_vote': user_vote,})

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'questions': page.object_list, 'page_obj': page})
def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=5)
    return render(request, 'hot.html', {'questions': page.object_list,'page_obj': page})

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    continue_url = request.GET.get('continue', 'index')
    form = LoginForm(data=request.POST or None, initial={'continue': continue_url})
    
    response = form.handle_request(request) if request.method == 'POST' else None
    return response or render(request, 'login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    form = SignUpForm(request.POST or None, request.FILES or None)
    
    response = form.handle_request(request) if request.method == 'POST' else None
    return response or render(request, 'signup.html', {'form': form})

@login_required
def settings(request):
    form = ProfileEditForm(
        request.POST or None, 
        request.FILES or None, 
        instance=request.user.profile
    )
    response = form.handle_request(request) if request.method == 'POST' else None
    return response or render(request, 'settings.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('index')

@login_required
def ask(request):
    form = AskQuestionForm(request.POST or None)
    response = form.handle_request(request) if request.method == 'POST' else None
    return response or render(request, 'ask.html', {'form': form})

@login_required
def answer_submit(request, question_id):
    form = AnswerForm(request.POST or None)
    response = form.handle_request(request, question_id) if request.method == 'POST' else None
    
    if response:
        return response
    
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question).order_by('-is_correct', '-created_at')
    page = paginate(answers, request, per_page=3)
    return render(request, 'single_question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'answer_form': form
    })

@require_POST
@login_required
def question_vote(request, question_id):
    is_like = request.POST.get('type') == 'like'
    return handle_question_vote(request, question_id, is_like)

@require_POST
@login_required
def answer_vote(request, answer_id):
    return handle_answer_vote(request, answer_id, request.POST.get('type') == 'like')

@require_POST
@login_required
def mark_correct_answer(request, question_id, answer_id):
    result, status = handle_correct_answer(request, question_id, answer_id)
    return JsonResponse(result, status=status)