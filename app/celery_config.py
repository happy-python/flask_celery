# coding:utf-8

# 使用 Redis 作为消息代理
BROKER_URL = 'redis://localhost:6379/15'
# 把任务结果存在 Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/15'
