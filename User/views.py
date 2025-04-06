from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.cache import cache
import json
import hashlib

from Post.models import Question, Answer, Tag
from Post.serializers import QuestionSerializer, AnswerSerializer
from User.pagination import CustomPageNumberPagination
from User.models import CustomUser, Reputation
from User.serializers import UserRegistrationSerializer, UserSerializer, ReputationSerializer


@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user":
                {"id":user.id,
                "username":user.username,
                "displayName":user.displayName,
                "avatar_url":user.avatar_url,
                "reputation":user.reputation,
                }
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        user = CustomUser.objects.get(email=email)
        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user":
                    {"id": user.id,
                     "username": user.username,
                     "displayName": user.displayName,
                     "avatar_url": user.avatar_url ,
                     "reputation": user.reputation,
                     }
            }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    try:
        if isinstance(request.user, AnonymousUser):
            return Response({'message': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({"error": "Invalid request, user not authenticated"}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def user(request):
    user = CustomUser.objects.get(id=request.user.id)
    return Response({
        "id": user.id,
         "username": user.username,
         "displayName": user.displayName,
         "avatar_url": user.avatar_url ,
         "reputation": user.reputation,
         }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def user_list(request):
    """
        Эндпоинт для получения списка пользователей.

        Параметры запроса:
          - page: номер страницы (по умолчанию 1)
          - page_size: количество объектов на странице (по умолчанию 12)
          - search: фильтрация по username или displayName
          - sort_by: варианты сортировки: 'reputation', 'newest', 'name'
    """
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params,sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"users_list:{key_hash}"

    cached_users = cache.get(cache_key)
    if cached_users:
        return Response(cached_users, status=status.HTTP_200_OK)

    queryset = CustomUser.objects.all()

    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(username__icontains=search)

    sort_by = request.query_params.get('sort_by')
    if sort_by:
        if sort_by == 'newest':
            queryset = queryset.order_by('-member_since')
        elif sort_by == 'reputation':
            queryset = queryset.order_by('-reputation')
        elif sort_by == 'name':
            queryset = queryset.order_by('username')
    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = UserSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout = 120)
    return paginated_response

@api_view(['GET'])
def user_details(request,id):
    cache_key = f"user_details:{id}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)
    try:
        user = CustomUser.objects.get(pk = id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    user_data = {
        "id": user.id,
        "username": user.username,
        "displayName": user.displayName,
        "email": user.email,
        "avatar_url": user.avatar_url ,
        "reputation": user.reputation,
        "location": user.location,
        "about": user.about,
        "member_since": user.member_since,
        "last_seen": user.last_login,
        "visit_streak": "Add in the future",
        "gold_badges": user.gold_badges,
        "silver_badges": user.silver_badges,
        "bronze_badges": user.bronze_badges,
    }
    cache.set(cache_key, user_data, timeout = 180)
    return Response(user_data,status = status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH','GET'])
def user_edit_get(request):
    if request.method == 'PATCH':
        """
            Ожидается, что файл аватара передаётся через request.FILES с ключом 'avatar'.
        """

        new_displayName = request.data.get('displayName')
        new_location = request.data.get('location')
        new_about = request.data.get('about')
        user = CustomUser.objects.get(id=request.user.id)
        avatar_file = request.FILES.get('avatar')
        if avatar_file:
            user.save_avatar(avatar_file,avatar_file.name)

        if new_displayName is not None and new_displayName != '' and new_displayName:
            user.displayName = new_displayName
        if new_location is not None and new_location != '' and new_location:
            user.location = new_location
        if new_about is not None and new_about != '' and new_about:
            user.about = new_about
        user.save()
        return Response({
            "id": user.id,
            "username": user.username,
            "displayName": user.displayName,
            "avatar_url": user.avatar_url ,
            "reputation": user.reputation,
            "location": user.location,
            "about": user.about,
            "member_since": user.member_since,
            "last_seen": user.last_login,
            "visit_streak": "Add in the future",
        }, status=status.HTTP_200_OK)
    elif request.method == 'GET':
        user_id = request.user.id
        cache_key = f"user_profile:{user_id}"
        cached_profile = cache.get(cache_key)
        if cached_profile:
            return JsonResponse(cached_profile, status=status.HTTP_200_OK)

        request_user = CustomUser.objects.get(id=request.user.id)

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
        cache.set(cache_key, user_data, timeout = 180)
        return Response(user_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_questions(request,id):
    """
    ** Query
    Parameters **:

    - `page`: integer(default: 1)
    - `page_size`: integer(default: 10)
    - `sort_by`: string(options: 'newest', 'votes', 'views')
    """
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params,sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"user_questions:{id}{key_hash}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)
    try:
        userr = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"error":"User not found on this id"}, status=status.HTTP_404_NOT_FOUND)
    queryset = Question.objects.filter(author=userr)
    sort_by = request.query_params.get('sort_by')
    if sort_by == 'votes':
        queryset = queryset.order_by('-vote_count')
    elif sort_by == 'views':
        queryset = queryset.order_by('-view_count')
    elif sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    else:
        queryset = queryset.order_by('-view_count')

    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = QuestionSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout = 120)
    return paginated_response


@api_view(['GET'])
def user_answers(request,id):
    """
    **Query Parameters**:

        - `page`: integer (default: 1)
        - `page_size`: integer (default: 10)
        - `sort_by`: string (options: 'newest', 'votes')
"""
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params,sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"user_questions:{id}{key_hash}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)

    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"error":"User not found on this id"}, status=status.HTTP_404_NOT_FOUND)
    queryset = Answer.objects.filter(author=user)
    sort_by = request.query_params.get('sort_by')
    if sort_by == 'votes':
        queryset = queryset.order_by('-vote_count')
    elif sort_by == 'views':
        queryset = queryset.order_by('-view_count')
    elif sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    else:
        queryset = queryset.order_by('-vote_count')

    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = AnswerSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout = 120)
    return paginated_response


@api_view(['GET'])
def user_tags(request,id):
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params, sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"user_questions:{id}{key_hash}"
    cached_response = cache.get(cache_key)
    if cached_response or cached_response == []:
        return Response(cached_response, status=status.HTTP_200_OK)
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    tags_data = []
    tags = Tag.objects.annotate(
        total_count=Count('questions'),
        user_count=Count('questions',filter=Q(questions__author__id=user.id))
        ).filter(user_count__gt=0)
    for tag in tags:
        tags_data.append({
            "id": tag.id,
            "name": tag.name,
            "score": tag.total_count,
            "posts": tag.user_count
        })
    cache.set(cache_key, tags_data, timeout = 120)
    return Response(tags_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_reputation_history(request, id):
    cache_key = f"user_reputation_history:{id}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    queryset = Reputation.objects.filter(user=user).order_by('-date')
    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = ReputationSerializer(paginated_queryset, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, paginated_response.data, timeout = 120)
    return paginated_response
