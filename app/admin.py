from django.contrib import admin
from .models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
# Register your models here.
admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)
