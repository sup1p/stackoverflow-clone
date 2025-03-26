from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password_repeat = serializers.CharField(style={'input_type': 'password_repeat'}, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password','password_repeat')
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        password = data['password']
        password_repeat = data['password_repeat']
        if password != password_repeat:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_repeat')
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user