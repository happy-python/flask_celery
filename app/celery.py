# coding:utf-8
from __future__ import absolute_import
from celery import Celery

celery = Celery('app', include=['app.tasks'])
celery.config_from_object('app.celery_config')
