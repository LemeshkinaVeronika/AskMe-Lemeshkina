from app.models import Tag, Profile
from django.db.models import Count

def common_context(request):
    return {
        'is_authenticated': request.user.is_authenticated,
        'popular_tags': Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10],
        'best_members': Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:10],
    }