# Generated by Django 5.1.7 on 2025-03-28 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_rename_avatar_path_customuser_avatar_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='display_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
