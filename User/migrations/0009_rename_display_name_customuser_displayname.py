# Generated by Django 5.1.7 on 2025-03-29 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0008_alter_customuser_display_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='display_name',
            new_name='displayName',
        ),
    ]
