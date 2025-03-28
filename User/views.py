from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from User.pagination import CustomPageNumberPagination
from User.models import CustomUser
from User.serializers import UserRegistrationSerializer, UserSerializer


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
                "display_name":user.display_name,
                "avatar_url":user.get_avatar_url() ,
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
                     "display_name": user.display_name,
                     "avatar_url": user.get_avatar_url() ,
                     "reputation": user.reputation,
                     }
            }, status=status.HTTP_201_CREATED)
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
         "display_name": user.display_name,
         "avatar_url": user.get_avatar_url() ,
         "reputation": user.reputation,
         }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def user_list(request):
    """
        Эндпоинт для получения списка пользователей.

        Параметры запроса:
          - page: номер страницы (по умолчанию 1)
          - page_size: количество объектов на странице (по умолчанию 12)
          - search: фильтрация по username или display_name
          - sort_by: варианты сортировки: 'reputation', 'newest', 'name'
    """
    queryset = CustomUser.objects.all()

    search = request.data.get('search')
    if search:
        queryset = queryset.filter(username__icontains=search)

    sort_by = request.data.get('sort_by')
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
    return Response(paginator.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

@api_view(['GET'])
def user_details(request,id):
    try:
        user = CustomUser.objects.get(pk = id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)
    return Response({
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.get_avatar_url() ,
        "reputation": user.reputation,
        "location": user.location,
        "about": user.bio,
        "member_since": user.member_since,
        "last_seen": user.last_login,
        "visit_streak": "Add in the future",
        "gold_badges": user.gold_badges,
        "silver_badges": user.silver_badges,
        "bronze_badges": user.bronze_badges,
    }, status = status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def user_edit(request):
    """
        Ожидается, что файл аватара передаётся через request.FILES с ключом 'avatar'.
    """

    new_display_name = request.data.get('display_name')
    new_location = request.data.get('location')
    new_about = request.data.get('about')
    user = CustomUser.objects.get(id=request.user.id)
    avatar_file = request.FILES.get('avatar')
    if avatar_file:
        user.save_avatar(avatar_file,avatar_file.name)

    if new_display_name is not None and new_display_name != '' and new_display_name:
        user.display_name = new_display_name
    if new_location is not None and new_location != '' and new_location:
        user.location = new_location
    if new_about is not None and new_about != '' and new_about:
        user.about = new_about
    user.save()
    return Response({
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.get_avatar_url() ,
        "reputation": user.reputation,
        "location": user.location,
        "about": user.bio,
        "member_since": user.member_since,
        "last_seen": user.last_login,
        "visit_streak": "Add in the future",
    }, status=status.HTTP_200_OK)
