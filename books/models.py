from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    status_choices = [
        ('to_read', 'To Read'),
        ('reading', 'Reading'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='to_read')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title