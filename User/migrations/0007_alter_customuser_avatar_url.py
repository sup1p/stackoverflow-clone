# Generated by Django 5.1.7 on 2025-03-28 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_alter_customuser_avatar_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar_url',
            field=models.CharField(blank=True, default='https://aenacihkjsxjdpkeqxja.supabase.co/storage/v1/object/public/stackoverflowcopyomar//IMG-20221013-WA0032.jpg', max_length=255, null=True),
        ),
    ]
