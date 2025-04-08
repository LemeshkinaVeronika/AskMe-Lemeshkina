from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')
    
    def hot(self):
        return self.annotate(
            total_likes=Count('questionlike', filter=Q(questionlike__is_like=True))
        ).order_by('-total_likes', '-created_at')  
    
    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-created_at')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete =models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    def __str__(self):
        return self.user.username
    
class Tag(models.Model):
    name = models.CharField(max_length= 50, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag_questions', args=[self.name])

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete =models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', args=[self.id])

    def total_likes(self):
        return self.questionlike_set.filter(is_like=True).count()
    def total_dislikes(self):
        return self.questionlike_set.filter(is_like=False).count()

    def answers_count(self):
        return self.answer_set.count()

class Answer(models.Model):
    text = models.TextField()

    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete = models.CASCADE)
    created_at =models.DateTimeField(default = timezone.now)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question.title}"

    def total_likes(self):
        return self.answerlike_set.filter(is_like = True).count()

    def total_dislikes(self):
        return self.answerlike_set.filter( is_like=False).count()
class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete =models.CASCADE)
    user = models.ForeignKey(Profile, on_delete= models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return f"{'Like' if self.is_like else 'Dislike'} for {self.question.title}"
    
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE)
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    is_like= models.BooleanField()

    class Meta:
        unique_together = ('answer', 'user')

    def __str__(self):
        return f"{'Like' if self.is_like else 'Dislike'} for answer #{self.answer.id}"

