"""
The best sentence

1 Don’t hate your enemy, or you will make wrong judgment.
2 I'm gonna make him an offer he can't refuse.
3 A friend should always underestimate your virtues and an enemy overestimate your faults.
4 You know...the world’s full of lonely people afraid to make the first move
5 I suffer that slight alone,because I’m not accepted by my own people,
    because i’m not like them either! So if I'm not black enough and if I'm not white enough,
    then tell me, Tony, what am I !?
6 whatever you do,do it a hundred percent.when you work,when you laugh,laugh,when you eat,eat like it's your last meal.

@author:StrongXiuXiu
@file: 这是定时任务的配置文件
@time:2021/11/15
"""

from __future__ import absolute_import
import os
from datetime import timedelta

REDIS_PASSWORD = "123456"
REDIS_PORT = "6379"
REDIS_DB = "14"
# 消息对列
broker_url = os.environ.get('CELERY_BROKER_URL',
                            'redis://:' + REDIS_PASSWORD + '@127.0.0.1' + ':' + REDIS_PORT + '/' + REDIS_DB)
# 存储
STORAGE_DB = "15"
result_backend = os.environ.get('CELERY_RESULT_BACKEND',
                                'redis://:' + REDIS_PASSWORD + '@127.0.0.1' + ':' + REDIS_PORT + '/' + STORAGE_DB)

# redis://:xxxxx@127.0.0.1:6379/2
result_serializer = 'json'
task_serializer = 'json'
accept_content = ['json']
# 时区
timezone = 'Asia/Shanghai'
# 过期时间
# event_queue_ttl = 5
# celery不回复结果
task_ignore_result = True

# 为防止内存泄漏，一个进程执行过N次之后杀死，建议是100次，我没听
worker_max_tasks_per_child = 10
# 错误 DatabaseWrapper objects created in a thread can only be used in that same thread
CELERY_TASK_ALWAYS_EAGER = True
worker_hijack_root_logger = False

# 需要执行任务的配置 # 声明定时任务
beat_schedule = {
    "task1": {
        "task": "system.tasks.celery_run",  # 执行的函数
        # "schedule": crontab(minute="*/1"),  # every minute 每分钟执行
        "schedule": timedelta(seconds=1),
        "args": ()  # # 任务函数参数
    },
}
