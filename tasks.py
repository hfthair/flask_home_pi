import time
from sv import celery

@celery.task
def add(x, y):
    print("------>")
    time.sleep(5)
    print("<--------------")
    return x + y

