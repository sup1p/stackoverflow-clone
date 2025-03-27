from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from User.models import CustomUser
from User.serializers import UserRegistrationSerializer


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
                "display_name":user.username,
                "avatar_url":user.avatar,
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
                     "display_name": user.username,
                     "avatar_url": user.avatar,
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
    user = request.user
    return Response({
        "id": user.id,
         "username": user.username,
         "display_name": user.username,
         "avatar_url": user.avatar,
         "reputation": user.reputation,
         }, status=status.HTTP_201_CREATED)
