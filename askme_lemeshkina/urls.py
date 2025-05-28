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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name = "index"),
    path('hot', views.hot, name = 'hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag_questions, name='tag'),
    path('ask', views.ask, name = 'ask'),
    path('question/<int:question_id>/answer/', views.answer_submit, name='answer_submit'),
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.settings, name='settings'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('question/<int:question_id>/vote/', views.question_vote, name='question_vote'),
    path('answer/<int:answer_id>/vote/', views.answer_vote, name='answer_vote'),
    path('question/<int:question_id>/mark-correct/<int:answer_id>/', views.mark_correct_answer, name='mark_correct_answer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    