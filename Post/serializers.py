from rest_framework import serializers
from Post.models import Tag, Question, Answer
from User.models import CustomUser, Reputation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'displayName', 'avatar_url', 'reputation']

class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    author = AuthorSerializer(read_only=True)
    tag_objects = TagSerializer(many=True, read_only=True, source='tags')
    class Meta:
        model = Question
        fields = ['id', 'title', 'author',
                  'tags', # for input (list of names)
                  'tag_objects',  # for output (full tag objects)
            'content', 'created_at', 'updated_at','vote_count','answer_count','view_count']

    def create(self, validated_data):
        tag_names = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)

        # Link or create tags
        tag_objs = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_objs.append(tag)

        question.tags.set(tag_objs)
        return question

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tag_names is not None:
            tag_objs = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tag_objs.append(tag)
            instance.tags.set(tag_objs)

        instance.save()
        return instance

class AnswerSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Answer
        fields = ['id','question_id','author', 'content', 'created_at', 'updated_at','vote_count','is_accepted']
