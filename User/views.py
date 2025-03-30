from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

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
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def user_details(request,id):
    try:
        user = CustomUser.objects.get(pk = id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)
    return Response({
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
    }, status = status.HTTP_200_OK)


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
        request_user = CustomUser.objects.get(id=request.user.id)
        return Response({
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
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_questions(request,id):
    """
    ** Query
    Parameters **:

    - `page`: integer(default: 1)
    - `page_size`: integer(default: 10)
    - `sort_by`: string(options: 'newest', 'votes', 'views')
    """
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
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def user_answers(request,id):
    """
    **Query Parameters**:

        - `page`: integer (default: 1)
        - `page_size`: integer (default: 10)
        - `sort_by`: string (options: 'newest', 'votes')
"""
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
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def user_tags(request,id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    tags_data = []
    tags = Tag.objects.all()
    for tag in tags:
        total_count = tag.questions.count()
        user_count = tag.questions.filter(author=user).count()

        if user_count > 0:
            tags_data.append({
                "id": tag.id,
                "name": tag.name,
                "score": total_count,
                "posts": user_count
            })

    return Response(tags_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_reputation_history(request, input_id):
    try:
        user = CustomUser.objects.get(id=input_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    queryset = Reputation.objects.filter(user=user).order_by('-date')
    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    serializer = ReputationSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)
