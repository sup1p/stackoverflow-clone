from time import timezone

from django.db import models
from StackOverflowCopy import settings

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)  # Описание тега (может быть пустым)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vote_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE,max_length=255, related_name='answers')
    content = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vote_count = models.IntegerField(default=0)
    is_accepted = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return f"Answer by userid:{self.author.id} on questionid:{self.question.id}"



class Vote(models.Model):
    VOTE_TYPES = (('upvote','Upvote'),('downvote','Downvote'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_votes', null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_votes', null=True, blank=True)
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'question', 'answer')

    def __str__(self):
        if self.question:
            return f"{self.user.username}, {self.vote_type}, Question {self.question.id}"
        elif self.answer:
            return f"{self.user.username}, {self.vote_type}, Answer {self.answer.id}"