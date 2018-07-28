# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=192)
    email = models.EmailField()
    is_deleted = models.BooleanField(default=False)
