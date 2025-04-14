from celery import shared_task
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

from User.models import CustomUser
import json
import hashlib
from User.pagination import CustomPageNumberPagination
from User.serializers import UserSerializer


@shared_task
def update_users_list_cache():
    print("inside update_users_list_cache 1")

    query_params = {
        "page": "1",
        "page_size": "12",
        "search": "",
        "sort_by": "reputation"
    }
    key_raw = json.dumps(query_params, sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"users_list:{key_hash}"

    class FakeRequest:
        def __init__(self, *args, **kwargs):
            self.query_params = query_params

        def build_absolute_uri(self):
            return "/api/users/"

    fake_request = FakeRequest(query_params)

    queryset = CustomUser.objects.all()
    queryset = queryset.order_by("-reputation")

    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, fake_request)
    serializer = UserSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout=180)
    print("inside update_users_list_cache 2, cache have been set")

@shared_task
def update_users_me_cache(user_id):
    print("inside update_users_profile_cache 1")
    cache_key = f"user_profile:{user_id}"

    try:
        request_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_data = {
        "id": request_user.id,
        "username": request_user.username,
        "displayName": request_user.displayName,
        "email": request_user.email,
        "avatar_url": request_user.avatar_url,
        "reputation": request_user.reputation,
        "location": request_user.location,
        "about": request_user.about,
        "member_since": request_user.member_since,
        "last_seen": request_user.last_login,
        "visit_streak": "Add in the future",
    }
    cache.set(cache_key, user_data, timeout=180)
    print("inside update_users_profile_cache 2")

@shared_task
def update_users_details_cache(request_user_id):
    print("DEBUG VALUE:", type(request_user_id))
    print("inside update_users_details_cache 1")
    try:
        cache_key = f"user_details:{request_user_id}"
    except Exception as ex:
        print(ex, "i couldnt perceive user_id")
    print("got cache_key by user_id")

    try:
        request_user = CustomUser.objects.get(id=request_user_id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_data = {
        "id": request_user.id,
        "username": request_user.username,
        "displayName": request_user.displayName,
        "email": request_user.email,
        "avatar_url": request_user.avatar_url,
        "reputation": request_user.reputation,
        "location": request_user.location,
        "about": request_user.about,
        "member_since": request_user.member_since,
        "last_seen": request_user.last_login,
        "visit_streak": "Add in the future",
        "gold_badges": request_user.gold_badges,
        "silver_badges": request_user.silver_badges,
        "bronze_badges": request_user.bronze_badges,
    }
    cache.set(cache_key, user_data, timeout = 180)
    print("inside update_users_details_cache 2")
