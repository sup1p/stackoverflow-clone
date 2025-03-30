import os

from django.db import models
from django.contrib.auth.models import AbstractUser
import io
from PIL import Image
from .supabase_client import upload_file_to_supabase
from Post.models import Tag



# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    about = models.TextField(null=True, blank=True)
    displayName = models.CharField(max_length=100,default="default_displayName")
    avatar_url = models.CharField(default="https://aenacihkjsxjdpkeqxja.supabase.co/storage/v1/object/public/stackoverflowcopyomar//IMG-20221013-WA0032.jpg",max_length=255, null=True, blank=True)

    def save_avatar(self, file_data, file_name):
        try:
            if not isinstance(file_data, io.BytesIO):
                file_data = io.BytesIO(file_data.read())

            file_data.seek(0)
            try:
                image = Image.open(file_data)
                image.verify()
                print(f"✅ Файл {file_name} успешно открыт и проверен. Формат: {image.format}")
            except Exception as e:
                print(f"❌ Ошибка при проверке изображения: {e}")
                return

            file_data.seek(0)

            full_path = f"avatars/{self.username}/{file_name}"

            success = upload_file_to_supabase(file_data, os.getenv('SUPABASE_BUCKET_NAME'), full_path)

            if success:
                supabase_url = os.getenv('SUPABASE_URL').strip('/')
                self.avatar_url = f"{supabase_url}/storage/v1/object/public/{os.getenv('SUPABASE_BUCKET_NAME')}/{full_path}"
                self.save()
                print(f"✅ Файл успешно загружен: {self.avatar_url}")
            else:
                raise Exception("❌ Ошибка загрузки файла на Supabase.")

        except Exception as e:
            print(f"Ошибка в save_avatar(): {e}")

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



class Reputation(models.Model):
    TYPE_CHOICES = [
        ('question_upvote', 'Question Upvote'),
        ('answer_upvote', 'Answer Upvote'),
        ('answer_accepted', 'Answer Accepted'),
        ('answer_downvote', 'Answer Downvote'),
        ('question_downvote', 'Question Downvote'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reputation_changes')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='!no data!')
    change = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.type} {self.change}"