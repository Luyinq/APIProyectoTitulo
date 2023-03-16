from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel


class Article(models.Model):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=500)

    def __str__(self):
        return self.title