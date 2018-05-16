CELERY_REDIS_HOST = 'localhost'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
BROKER_URL = '{}://{}/{}'.format('redis', CELERY_REDIS_HOST, 1)
INSTALLED_APPS = []
