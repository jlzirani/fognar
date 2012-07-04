# Copyright 2012, RespLab. All rights reserved.

from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from re import sub

class Page(models.Model):
    num = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()


class Document(models.Model):
    name = models.TextField()
    description = models.TextField()
    uploader = models.ForeignKey(User)
    # a course, a discussion, a group whatever
    refer_oid = models.PositiveIntegerField()
    refer_content = models.ForeignKey(ContentType)
    referer = GenericForeignKey('refer_content', 'refer_oid')

    size = models.PositiveIntegerField(null=True, default=0)
    words = models.PositiveIntegerField(null=True, default=0)
    pages = models.PositiveIntegerField(null=True, default=0)
    date = models.DateTimeField(auto_now=True, null=False)

    def pretty_name(self):
        name = sub(r'[^-_a-z]', '', self.name.lower().replace(' ', '_'))
        if not name.endswith('.pdf'):
            name += '.pdf'
        return name


class PendingDocument(models.Model):
    doc = models.ForeignKey(Document)
    state = models.CharField(max_length=30)
    url = models.CharField(max_length=255)
    done = models.PositiveIntegerField(default=0)