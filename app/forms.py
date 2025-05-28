from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Profile
from django.shortcuts import redirect, get_object_or_404
from .models import Question, Answer, Tag, Profile, User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control w-50',
            'placeholder': 'Enter your login or email'
        }),
        label="Login or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-50',
            'placeholder': 'Enter your password'
        }),
        label="Password",
        strip=False
    )
    error_messages = {
        'invalid_login': "Invalid login or password",
    }
    
    def handle_request(self, request):
        if self.is_valid():
            user = self.get_user()
            auth_login(request, user)
            return redirect(self.cleaned_data.get('continue', 'index'))
        else:
            messages.error(request, "Invalid username or password.")
        return None
    
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control w-50',
            'placeholder': 'Enter your username'
        }),
        label="Username",
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-50',
            'placeholder': 'Enter your email'
        }),
        label="Email",
        help_text="Required. Enter a valid email address."
    )
    nickname = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control w-50',
            'placeholder': 'Enter your nickname'
        }),
        label="Nickname",
        help_text="Required. 30 characters or fewer."
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control w-50'}),
        label="Profile Picture"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password1', 'password2', 'avatar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].error_messages = {
            'required': 'Please enter your password',
            'password_too_short': 'Password is too short',
            'password_too_common': 'Password is too common',
        }
        self.fields['password2'].error_messages = {
            'required': 'Please confirm your password',
            'password_mismatch': 'Passwords do not match',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname__iexact=nickname).exists():
            raise ValidationError("This nickname is already in use.")
        return nickname
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = user.profile
            profile.nickname = self.cleaned_data['nickname']
            if self.cleaned_data['avatar']:
                profile.avatar = self.cleaned_data['avatar']
            profile.save()
        return user
    def handle_request(self, request):
        if self.is_valid():
            user = self.save()
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Please correct the errors below.")
        return None

    
class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control w-50'}),
        label="Username"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control w-50'}),
        label="Email"
    )
    nickname = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control w-50'}),
        label="Nickname"
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control w-50'}),
        label="Change Profile Picture"
    )
    
    class Meta:
        model = Profile
        fields = ('username', 'email', 'nickname', 'avatar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['nickname'].initial = self.instance.nickname
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError("This username is already in use.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError(_("This email is already in use."))
        return email
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname__iexact=nickname).exclude(user=self.instance.user).exists():
            raise ValidationError(_("This nickname is already in use."))
        return nickname
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data['email']
        profile.nickname = self.cleaned_data['nickname']
        if self.cleaned_data['avatar']:
            profile.avatar = self.cleaned_data['avatar']
        if commit:
            profile.user.save()
            profile.save()
        return profile
    def handle_request(self, request):
        if self.is_valid():
            self.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('settings')
        else:
            messages.error(request, "Please correct the errors below.")
        return None

class AskQuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags'
        }),
        help_text="Separate tags with commas"
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the title'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your question',
                'rows': 5
            }),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
        
        for tag_name in tag_names:
            if len(tag_name) > 50:
                raise ValidationError(f"Tag '{tag_name}' is too long (maximum 50 characters).")
        
        return tag_names

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        
        if commit:
            question.save()
            
            tag_names = self.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            
            question.save()
        
        return question

    def handle_request(self, request):
        if self.is_valid():
            question = self.save(commit=False, author=request.user.profile)
            question.save()
            tag_names = self.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                question.tags.add(tag)
            
            return redirect('question', question_id=question.id)
        return None


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your answer',
                'rows': 5
            }),
        }
    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        if author:
            answer.author = author
        if question:
            answer.question = question
        
        if commit:
            answer.save()
        
        return answer
    def handle_request(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        if self.is_valid():
            answer = self.save(commit=False, author=request.user.profile, question=question)
            answer.save()
            return redirect(f"{question.get_absolute_url()}#answer-{answer.id}")
        return None
