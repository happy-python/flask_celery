# coding:utf-8
from app import create_app
from flask_mail import Mail
from app.celery import celery
import random, time


# 任何需要作为后台任务的函数都需要使用 celery.task 装饰器装饰
@celery.task
def async_send_email(msg):
    app = create_app()
    # 注意：Flask-Mail 需要在应用的上下文中运行，因此在调用 send() 之前需要创建一个应用上下文
    with app.app_context():
        # 此异步调用返回值并不保留，因此应用本身无法知道是否调用成功或者失败。运行这个示例的时候，需要检查 Celery worker 的输出来排查发送邮件过程是否有问题
        Mail(app).send(msg)


@celery.task(bind=True)
def long_task(self):
    total = random.randint(10, 50)
    for i in range(total):
        # 自定义状态 state
        self.update_state(state=u'处理中', meta={'current': i, 'total': total})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'result': u'完成'}
