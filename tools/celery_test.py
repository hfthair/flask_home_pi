import time
from flask import Flask
from celery import Celery

# app = Flask(__name__)
# app.config['BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery('proj', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')
# celery = Celery(app.name, broker=app.config['BROKER_URL'])
# celery.conf.update(app.config)

@celery.task
def add(x, y):
    print("------>")
    time.sleep(5)
    print("<--------------")
    return x + y

# pipenv install "celery[redis]"
# celery -A celery_test.celery worker  --pool=solo -l info
