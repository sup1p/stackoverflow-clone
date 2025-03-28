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

    bio = models.TextField(null=True, blank=True)
    display_name = models.CharField(max_length=100,default='')
    avatar_url = models.CharField(default="https://aenacihkjsxjdpkeqxja.supabase.co/storage/v1/object/public/stackoverflowcopyomar//IMG-20221013-WA0032.jpg",max_length=255, null=True, blank=True)

    def save_avatar(self, file_data, file_name):
        try:
            # Проверяем тип файла
            if not isinstance(file_data, io.BytesIO):
                # Читаем файл как байты и конвертируем в BytesIO
                file_data = io.BytesIO(file_data.read())

            # Перемещаем указатель в начало файла
            file_data.seek(0)

            # 🔍 Сохранение файла локально для проверки (сохранится в директории с проектом)
            with open(f"debug_{file_name}", "wb") as debug_file:
                debug_file.write(file_data.getvalue())

            # Теперь проверяем, что файл не повреждён
            try:
                image = Image.open(file_data)
                image.verify()  # Проверка на повреждения
                print(f"✅ Файл {file_name} успешно открыт и проверен. Формат: {image.format}")
            except Exception as e:
                print(f"❌ Ошибка при проверке изображения: {e}")
                return

            # Перемещаем указатель обратно в начало
            file_data.seek(0)

            # Генерируем полный путь для хранения файла в Supabase
            full_path = f"avatars/{self.username}/{file_name}"

            # Загружаем файл на Supabase
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
