# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.cache import cache

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=192)
    email = models.EmailField()
    is_deleted = models.BooleanField(default=False)

    def cache_key(self, name):
        return f'user:{self.id}:' + name

    @property
    def posts(self):
        return self.post_set.filter(is_deleted=False)

    @property
    def reposts(self):
        return self.repost_set.filter(is_deleted=False, post__is_deleted=False)

    @property
    def cache_key_post_count(self):
        return self.cache_key_prefix + 'post_count'

    @property
    def post_count(self):
        if not hasattr(self, '_post_count'):
            self._post_count = cache.get(self.cache_key('post_count'))
            if self._post_count is None:
                self.cache_post_count()
        return self._post_count

    @property
    def repost_count(self):
        if not hasattr(self, '_repost_count'):
            self._repost_count = cache.get(self.cache_key('repost_count'))
            if self._repost_count is None:
                self.cache_repost_count()
        return self._repost_count

    def cache_post_count(self):
        self._post_count = self.posts.count()
        cache.set(self.cache_key('post_count'), self._post_count, settings.CACHE_EXPIRE)

    def cache_repost_count(self):
        self._repost_count = self.reposts.count()
        cache.set(self.cache_key('repost_count'), self._repost_count, settings.CACHE_EXPIRE)
