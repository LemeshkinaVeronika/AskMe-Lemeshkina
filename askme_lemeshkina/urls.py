"""
URL configuration for askme_lemeshkina project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name = "index"),
    path('hot', views.hot, name = 'hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag_questions, name='tag'),
    path('ask', views.ask, name = 'ask'),
    path('ask/submit/', views.ask_submit, name='ask_submit'),
    path('question/<int:question_id>/answer/', views.answer_submit, name='answer_submit'),
    path('login', views.login, name = 'login'),
    path('signup', views.signup, name = 'signup'),
    path('settings', views.settings, name = 'settings'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('signup/submit/', views.signup_submit, name='signup_submit'),
    path('settings/submit/', views.settings_submit, name='settings_submit'),
]
