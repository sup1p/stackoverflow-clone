import os

from django.db import models
from django.contrib.auth.models import AbstractUser

from .supabase_client import upload_file_to_supabase, generate_presigned_url
from Post.models import Tag


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    bio = models.TextField(null=True, blank=True)
    display_name = models.CharField(max_length=100,default='')
    avatar_url = models.CharField(max_length=255, null=True, blank=True)

    def save_avatar(self, file_data, file_name):
        full_path = f"avatars/{self.username}/{file_name}"
        if upload_file_to_supabase(file_data, os.getenv('SUPABASE_BUCKET_NAME'), full_path):
            self.avatar_url = full_path
            self.save()

    def get_avatar_url(self):
        if self.avatar_url is None:
            return generate_presigned_url(
                os.getenv('DEFAULT_AVATAR_PATH'),
                os.getenv('SUPABASE_BUCKET_NAME')
            )

        return generate_presigned_url(self.avatar_url, os.getenv('SUPABASE_BUCKET_NAME'))

    reputation = models.IntegerField(default=1)
    location = models.CharField(max_length=255,null=True, blank=True)
    member_since = models.DateTimeField(auto_now_add=True)
    gold_badges = models.PositiveIntegerField(default=0)
    silver_badges = models.PositiveIntegerField(default=0)
    bronze_badges = models.PositiveIntegerField(default=0)
    question_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    top_tags = models.ManyToManyField(Tag, related_name='users', blank=True)

    def __str__(self):
        return self.username
