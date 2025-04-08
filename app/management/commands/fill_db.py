import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction, IntegrityError
from faker import Faker
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.utils import timezone

class Command(BaseCommand):
    help = 'Fill the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Fill ratio for database population')

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()

        self.stdout.write(f"Filling database with ratio {ratio}...")

        existing_users_count = User.objects.count()
        if existing_users_count < ratio:
            self.stdout.write(f"Creating {ratio - existing_users_count} users...")
            new_users = []
            for i in range(ratio - existing_users_count):
                username = f"user_{uuid.uuid4().hex[:8]}"
                email = f"{username}@example.com"
                new_users.append(User(
                    username=username,
                    email=email,
                    password=make_password('password')
                ))
            
            User.objects.bulk_create(new_users, batch_size=1000)
        
        users = list(Profile.objects.select_related('user').all())

        self.stdout.write(f"Creating {ratio} tags...")
        tags = []
        existing_tags_count = Tag.objects.count()
        if existing_tags_count < ratio:
            self.stdout.write(f"Creating {ratio - existing_tags_count} tags...")
            tags = []
            existing_tags = set(Tag.objects.values_list('name', flat=True))
            
            for i in range(ratio - existing_tags_count):
                attempt = 0
                while True:
                    attempt += 1
                    if attempt < 5:
                        tag_name = '_'.join(fake.words(nb=random.randint(2, 3))).upper()[:50]
                    else:
                        tag_name = f"TAG_{uuid.uuid4().hex[:6]}"
                    
                    if tag_name not in existing_tags:
                        tags.append(Tag(name=tag_name))
                        existing_tags.add(tag_name)
                        break
                    
                    if attempt > 10:
                        tag_name = f"TAG_{i}_{uuid.uuid4().hex[:4]}"
                        tags.append(Tag(name=tag_name))
                        break
            
            Tag.objects.bulk_create(tags, batch_size=1000)
        tags = list(Tag.objects.all())

        questions_count = ratio * 10
        existing_questions_count = Question.objects.count()
        if existing_questions_count < questions_count:
            self.stdout.write(f"Creating {questions_count - existing_questions_count} questions...")
            questions = []
            for i in range(questions_count - existing_questions_count):
                author = random.choice(users)
                title = fake.sentence()[:-1] + '?'
                text = '\n\n'.join(fake.paragraphs())
                questions.append(Question(
                    title=title,
                    text=text,
                    author=author,
                    created_at=timezone.make_aware(fake.date_time_between(
                        start_date='-1y', 
                        end_date='now'
                    ))
                ))
            
            Question.objects.bulk_create(questions, batch_size=1000)
        
        questions = list(Question.objects.all())

        for question in questions:
            if not question.tags.exists():
                question.tags.set(random.sample(tags, min(3, len(tags))))

        answers_count = ratio * 100
        existing_answers_count = Answer.objects.count()
        if existing_answers_count < answers_count:
            self.stdout.write(f"Creating {answers_count - existing_answers_count} answers...")
            answers = []
            for i in range(answers_count - existing_answers_count):
                question = random.choice(questions)
                author = random.choice(users)
                text = '\n\n'.join(fake.paragraphs())
                answers.append(Answer(
                    text=text,
                    question=question,
                    author=author,
                    created_at=timezone.make_aware(fake.date_time_between(
                        start_date=question.created_at, 
                        end_date='now'
                    )),
                    is_correct=random.choice([True, False])
                ))
            
            Answer.objects.bulk_create(answers, batch_size=1000)
        
        answers = list(Answer.objects.all())

        self.create_votes(ratio, users, questions, answers)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled database with ratio {ratio}'))

    def create_votes(self, ratio, users, questions, answers):
        question_likes = []
        for _ in range(ratio * 200):
            question = random.choice(questions)
            user = random.choice(users)
            question_likes.append(QuestionLike(
                question=question,
                user=user,
                is_like=random.choice([True, False])
            ))
        
        QuestionLike.objects.bulk_create(question_likes, batch_size=1000, ignore_conflicts=True)

        answer_likes = []
        for _ in range(ratio * 200):
            answer = random.choice(answers)
            user = random.choice(users)
            answer_likes.append(AnswerLike(
                answer=answer,
                user=user,
                is_like=random.choice([True, False])
            ))
        
        AnswerLike.objects.bulk_create(answer_likes, batch_size=1000, ignore_conflicts=True)