from celery import shared_task
from django.core.cache import cache
from Post.models import Question
import json
import hashlib
from Post.pagination import CustomPageNumberPagination
from Post.serializers import QuestionSerializer


@shared_task
def update_question_list_cache():
    print("inside update_question_list_cache 1")

    query_params = {
        "page": "1",
        "page_size": "10",
        "sort_by": "newest"
    }
    key_raw = json.dumps(query_params, sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"question_list:{key_hash}"
    print(key_hash)

    class FakeRequest:
        def __init__(self, *args, **kwargs):
            self.query_params = query_params

        def build_absolute_uri(self):
            return "/api/questions/"

    fake_request = FakeRequest(query_params)

    queryset = Question.objects.all()
    queryset = queryset.order_by('-created_at')

    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, fake_request)
    serializer = QuestionSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout=60)
    print("inside update_question_list_cache 2, cache have been set")