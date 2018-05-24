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


class Repost(models.Model):
    user = models.ForeignKey('users.User')
    origin = models.ForeignKey('posts.Product', related_name='product_set')
    created_at = models.DateTimeField(auto_now_add=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model)


class ProductQuerySet(models.QuerySet):
    def prefetch(self):
        prefetch_repost = models.Prefetch('repost__origin',
                                          queryset=Product.objects.all().select_related('user'),
                                          to_attr='_origin')
        queryset = self.prefetch_related(prefetch_repost)
        return queryset.select_related('user', 'post', 'repost')


class Product(models.Model):
    user = models.ForeignKey('users.User')
    post = models.ForeignKey('posts.Post', null=True)
    repost = models.ForeignKey('posts.Repost', null=True)

    objects = ProductManager()

    @classmethod
    def fetch_list(cls, **kwargs):
        prefetch_repost = models.Prefetch('repost__origin',
                                          queryset=cls.objects.all().select_related('user'),
                                          to_attr='_origin')

        products = cls.objects.filter(**kwargs)
        products = products.prefetch_related(prefetch_repost)

        return products.select_related('user', 'post', 'repost')

    @classmethod
    def seed(cls):
        users = [User(name='test{}'.format(i), email='test{}@example.com'.format(i))
                 for i in range(10)]
        User.objects.bulk_create(users)
        for user in User.objects.all():
            post = Post.objects.create(user=user, title='test{}'.format(user.id))
            Product.objects.create(user=user, post=post)
        user = User.objects.create(name='reposter', email='reposter@example.com')
        for product in Product.objects.all():
            repost = Repost.objects.create(user=user, origin=product)
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
