from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Question, QuestionLike, Profile, Answer, AnswerLike
from django.db import transaction
from django.db.models import Count, Case, When, IntegerField

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


def handle_question_vote(request, question_id, is_like):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    try:
        with transaction.atomic():  
            question = Question.objects.select_for_update().get(pk=question_id)  
            profile = Profile.objects.get(user=request.user)
            vote, created = QuestionLike.objects.get_or_create(
                question=question,
                user=profile,
                defaults={'is_like': is_like}
            )
            if not created:
                if vote.is_like == is_like:
                    vote.delete()
                    new_vote_state = None
                else:
                    vote.is_like = is_like
                    vote.save()
                    new_vote_state = is_like
            else:
                new_vote_state = is_like
            
            
            counts = Question.objects.filter(pk=question_id).annotate(
                likes_count=Count(
                    Case(
                        When(questionlike__is_like=True, then=1),
                        output_field=IntegerField()
                    )
                ),
                dislikes_count=Count(
                    Case(
                        When(questionlike__is_like=False, then=1),
                        output_field=IntegerField()
                    )
                )
            ).first()
            
            return JsonResponse({
                'total_likes': counts.likes_count if counts else 0,
                'total_dislikes': counts.dislikes_count if counts else 0,
                'user_vote': new_vote_state
            })
            
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def handle_answer_vote(request, answer_id, is_like):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    try:
        with transaction.atomic():
            answer = Answer.objects.select_for_update().get(pk=answer_id)
            profile = Profile.objects.get(user=request.user)
            
            vote, created = AnswerLike.objects.get_or_create(
                answer=answer,
                user=profile,
                defaults={'is_like': is_like}
            )
            
            if not created:
                if vote.is_like == is_like:
                    vote.delete()
                    new_vote_state = None
                else:
                    vote.is_like = is_like
                    vote.save()
                    new_vote_state = is_like
            else:
                new_vote_state = is_like
            
            counts = Answer.objects.filter(pk=answer_id).annotate(
                likes_count=Count(
                    Case(
                        When(answerlike__is_like=True, then=1),
                        output_field=IntegerField()
                    )
                ),
                dislikes_count=Count(
                    Case(
                        When(answerlike__is_like=False, then=1),
                        output_field=IntegerField()
                    )
                )
            ).first()
            
            return JsonResponse({
                'total_likes': counts.likes_count if counts else 0,
                'total_dislikes': counts.dislikes_count if counts else 0,
                'user_vote': new_vote_state
            })
            
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def handle_correct_answer(request, question_id, answer_id):
    try:
        with transaction.atomic():
            question = Question.objects.select_for_update().get(pk=question_id)
            if question.author.user != request.user:
                return {'error': 'Only question author can mark correct answer'}, 403
            
            answer = Answer.objects.select_for_update().get(pk=answer_id, question=question)
            new_state = not answer.is_correct
            
            if new_state:
                Answer.objects.filter(question=question).exclude(pk=answer_id).update(is_correct=False)
            
            answer.is_correct = new_state
            answer.save()
            
            return {
                'success': True,
                'is_correct': new_state,
                'answer_id': answer_id
            }, 200
            
    except (Question.DoesNotExist, Answer.DoesNotExist):
        return {'error': 'Not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500
    

def add_vote_context(request, question, answers):
    context = {
        'question': question,
        'answers': answers,
        'user_vote': None
    }
    
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            q_vote = QuestionLike.objects.filter(
                question=question, 
                user=profile
            ).first()
            context['user_vote'] = q_vote.is_like if q_vote else None
            
            answer_votes = {
                v.answer_id: v.is_like
                for v in AnswerLike.objects.filter(
                    answer__in=answers,
                    user=profile
                )
            }
            
            for answer in answers:
                answer.user_vote = answer_votes.get(answer.id)
                
        except Profile.DoesNotExist:
            pass
    
    return context