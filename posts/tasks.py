# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from contextlib import contextmanager
from django.core.cache import cache
from elasticsearch import Elasticsearch
from fuga.celery import app


LOCK_EXPIRE = 5


@contextmanager
def task_lock(lock_id, oid):
    yield cache.add(lock_id, oid, LOCK_EXPIRE)


@app.task(bind=True)
def follow(self, x, y):
    lock_id = '{}-{}'.format(self.name, x)
    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            elastic = Elasticsearch()
            ctx = 'ctx._source.target_users'
            source = 'if (!{ctx}.contains(params.user_id)) {ctx}.add(params.user_id)'
            elastic.update(index='user',
                           doc_type='_doc',
                           id=x,
                           body={
                               'script': {
                                   'source': source.format(ctx=ctx),
                                   'params': {
                                       'user_id': y,
                                   }
                               }
                           })
            return True

        follow.apply_async(args=(x, y), countdown=LOCK_EXPIRE)


@app.task(bind=True)
def unfollow(self, x, y):
    lock_id = '{}-{}'.format(self.name, x)
    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            elastic = Elasticsearch()
            ctx = 'ctx._source.target_users'
            source = '{ctx}.removeIf(elem -> elem == params.user_id)'
            elastic.update(index='user',
                           doc_type='_doc',
                           id=x,
                           body={
                               'script': {
                                   'source': source.format(ctx=ctx),
                                   'params': {
                                       'user_id': y,
                                   }
                               }
                           })
            return True

        unfollow.apply_async(args=(x, y), countdown=LOCK_EXPIRE)
