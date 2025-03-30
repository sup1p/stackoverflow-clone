from django.contrib.auth import get_user_model
from User.models import Reputation, CustomUser

User = get_user_model()

def add_reputation(user_id:int, rep_type:str, change:int, description:str):
    try:
        user = CustomUser.objects.get(id=user_id)
        Reputation.objects.create(user=user, type=rep_type, change=change, description=description)
        user.reputation += change
        user.save()
    except CustomUser.DoesNotExist:
        pass