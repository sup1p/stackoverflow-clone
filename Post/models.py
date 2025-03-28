from django.db import models
from StackOverflowCopy import settings

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=100)

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

class QuestionVote(models.Model):
    VOTE_TYPES = (('upvote','Upvote'),('downvote','Downvote'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='question_votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username}, {self.vote_type}, {self.question.title}"