from rest_framework import serializers
from Post.models import Tag, Question, Answer
from User.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'display_name', 'avatar_url', 'reputation']

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()

class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'title', 'author', 'tags', 'content', 'created_at', 'updated_at','vote_count','answer_count','view_count']

class AnswerSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Answer
        fields = ['id','question_id','author', 'content', 'created_at', 'updated_at','vote_count','is_accepted']