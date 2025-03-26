from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    bio = models.TextField(null=True, blank=True)
    pictire = models.ImageField(upload_to="pictire/", null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    reputation = models.IntegerField(default=0)
    question_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.username
