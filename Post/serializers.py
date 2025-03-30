from rest_framework import serializers
from Post.models import Tag, Question, Answer
from User.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'displayName', 'avatar_url', 'reputation']

class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'author',
            'tag_names',  # input: tag names (write-only)
            'tags',       # output: full tag objects
            'content', 'created_at', 'updated_at',
            'vote_count', 'answer_count', 'view_count'
        ]

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        question = Question.objects.create(**validated_data)
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        question.tags.set(tags)
        return question

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tag_names is not None:
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            instance.tags.set(tags)
        instance.save()
        return instance

class AnswerSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Answer
        fields = ['id','question_id','author', 'content', 'created_at', 'updated_at','vote_count','is_accepted']
