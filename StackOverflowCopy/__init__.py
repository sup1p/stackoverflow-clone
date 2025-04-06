from .celery import app as celery_app
__all__ = ['celery_app']


#  running -> 1)"redis server"
#             2)"python manage.py runserver"
#             3)"celery -A myproject worker --loglevel-info"