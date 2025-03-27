import os

from django.db import models
from django.contrib.auth.models import AbstractUser

from .supabase_client import upload_file_to_supabase, generate_presigned_url


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    bio = models.TextField(null=True, blank=True)
    avatar_path = models.CharField(max_length=255, null=True, blank=True)

    def save_avatar(self, file_data, file_name):
        full_path = f"avatars/{self.username}/{file_name}"
        if upload_file_to_supabase(file_data, os.getenv('SUPABASE_BUCKET_NAME'), full_path):
            self.avatar_path = full_path
            self.save()

    def get_avatar_url(self):
        if not self.avatar_path:
            return generate_presigned_url(
                os.getenv('DEFAULT_AVATAR_PATH'),
                os.getenv('SUPABASE_BUCKET_NAME')
            )

        return generate_presigned_url(self.avatar_path, os.getenv('SUPABASE_BUCKET_NAME'))

    reputation = models.IntegerField(default=0)
    question_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)

    def __str__(self):
        return self.username
