# coding:utf-8
from flask import redirect, url_for, render_template, flash, request, session, jsonify
from flask_mail import Message
from app.tasks import long_task, async_send_email
from app import create_app

app = create_app()


@app.route('/longtask')
def longtask():
    # 开启异步任务
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskprogress', task_id=task.id)}


@app.route('/progress/<task_id>')
def taskprogress(task_id):
    # 获取异步任务结果
    task = long_task.AsyncResult(task_id)
    # 等待处理
    if task.state == 'PENDING':
        response = {'state': task.state, 'current': 0, 'total': 1}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'current': task.info.get('current', 0), 'total': task.info.get('total', 1)}
        # 处理完成
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # 后台任务出错
        response = {'state': task.state, 'current': 1, 'total': 1}
    return jsonify(response)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    msg = Message('Hello from Flask', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = 'This is a test email sent from a background Celery task.'
    if request.form['submit'] == 'Send':
        # 立即发送
        # delay 是 apply_async 的快捷快捷方式
        # 相比于 delay，当使用 apply_async 时，我们能够对后台任务的执行方式有更多的控制。例如任务在何时执行
        # delay 和 apply_async 的返回值是一个 AsyncResult 的对象。通过该对象，能够获得任务的状态信息
        async_send_email.delay(msg)
        flash('Sending email to {0}'.format(email))
    else:
        # 1分钟后发送
        async_send_email.apply_async(args=[msg], countdown=60)
        flash('An email will be sent to {0} in one minute'.format(email))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
