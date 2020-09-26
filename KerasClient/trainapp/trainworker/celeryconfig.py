import os

# Redisストアデータベースへの接続情報
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
CONNECT_REDIS_URL = os.environ["CONNECT_REDIS_URL"]
CONNECT_REDIS_URL = CONNECT_REDIS_URL.replace("{REDIS_HOST}", REDIS_HOST)
CONNECT_REDIS_URL = CONNECT_REDIS_URL.replace("{REDIS_PORT}", REDIS_PORT)

broker_url = CONNECT_REDIS_URL
result_backend = CONNECT_REDIS_URL

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Tokyo"
enable_utc = True
include = ["%s.tasks" % os.environ["CELERY_PROJECT"]]

CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = False
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_BROKER_POOL_LIMIT = None
CELERY_RESULT_SERIALIZER = 'json'