# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from time import sleep
from celery import Celery
from . import settings

app = Celery('app')
app.config_from_object('app:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task
def add(x, y):
    sleep(5)
    return x + y

for i in range(20):
    add.delay(i, 1)
