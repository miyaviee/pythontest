# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models, connection
from users.models import User


class Post(models.Model):
    user = models.ForeignKey('users.User')
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    is_deleted = models.BooleanField(default=False)


class Repost(models.Model):
    user = models.ForeignKey('users.User')
    post = models.ForeignKey('Post', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model)

    def fetch_list(self, **kwargs):
        queryset = self.get_queryset().filter(**kwargs)
        return queryset.fetch_list()


class ProductQuerySet(models.QuerySet):
    def fetch_list(self):
        queryset = self.filter(user__is_deleted=False) \
            .exclude(post__is_deleted=True) \
            .exclude(repost__is_deleted=True) \
            .exclude(repost__user__is_deleted=True)
        return queryset

    def prefetch(self):
        return self.prefetch_post().prefetch_repost()

    def prefetch_post(self):
        queryset = self.select_related('post', 'post__user')
        return queryset

    def prefetch_repost(self):
        queryset = self.select_related('repost', 'repost__user')
        return queryset


class Product(models.Model):
    user = models.ForeignKey('users.User')
    post = models.ForeignKey('posts.Post', null=True)
    repost = models.ForeignKey('posts.Repost', null=True)

    objects = ProductManager()

    @classmethod
    def seed(cls):
        users = [User(name=f'test{i}', email='test{i}@example.com') for i in range(10)]
        User.objects.bulk_create(users)
        for user in User.objects.all():
            post = Post.objects.create(user=user, title='test{}'.format(user.id))
            Product.objects.create(user=user, post=post)

        user = User.objects.create(name='reposter', email='reposter@example.com')
        for product in Product.objects.all():
            repost = Repost.objects.create(user=user, post=product.post)
            Product.objects.create(user=user, repost=repost)

    @classmethod
    def raw_data(cls):
        basequery = """
        select
            `p`.`id`,
            `u`.`id`,
            `p`.`created_at`,
            {type}
        from
            `{table_name}` as `p`
        join
            `users_user` as `u`
            on `p`.`user_id` = `u`.`id`
        where
            `p`.`created_at` between
            %s and %s
        """
        now = datetime.now()
        params = [now, now]
        raw_data = []
        with connection.cursor() as cursor:
            query = basequery.format(type=1, table_name='posts_post')
            cursor.execute(query, params=params)
            columns = ['post_id', 'user_id', 'created_at', 'type']
            raw_data.extend([dict(zip(columns, row)) for row in cursor.fetchall()])

            query = basequery.format(type=2, table_name='posts_repost')
            cursor.execute(query, params=params)
            columns = ['repost_id', 'user_id', 'created_at', 'type']
            raw_data.extend([dict(zip(columns, row)) for row in cursor.fetchall()])

        return raw_data
