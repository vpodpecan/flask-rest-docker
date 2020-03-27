import os
import time
from celery import Celery

from googletrans import Translator


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


# @celery.task(name='tasks.pow2')
# def pow2(x):
#     time.sleep(1)
#     return x**2

@celery.task(name='tasks.translate')
def translate(text, lang):
    return Translator().translate(text, dest=lang).text
