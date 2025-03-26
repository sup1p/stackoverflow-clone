from django.contrib import admin

from User.models import CustomUser

admin.site.register(CustomUser)