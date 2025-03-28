from rest_framework import serializers
from Post.models import Tag, Question
from User.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username','display_name','avatar_url','reputation']

class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'title', 'author', 'tags', 'content', 'created_at', 'updated_at','vote_count','answer_count','view_count']