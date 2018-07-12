echo off
echo start from pipenv shell
pause

start "redis server" /d "C:\Program Files\Redis" redis-server redis.windows.conf
echo starting celery...
celery -A tasks.celery worker  --pool=solo -l info
