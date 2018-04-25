from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver

class Tasklist(models.Model):
    owner = models.ForeignKey(
        'auth.User',
        related_name='tasklists',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    available_to = models.ManyToManyField(User, blank=True, default=owner)
    def __str__(self):
        return "{}".format(self.name)

class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return "{}".format(self.name)

class Task(models.Model):
    owner = models.ForeignKey(
        'auth.User',
        related_name='tasks',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    available_to = models.ManyToManyField(User, blank=True, default=owner)
    description = models.TextField(null=True, max_length=1000, blank=True)
    completed = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    date_modified = models.DateField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, default='n')
    tasklist = models.ForeignKey(Tasklist, related_name='tasks', on_delete=models.CASCADE)

    PRIORITY = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    )

    priority = models.CharField(max_length=1, choices=PRIORITY, default='n')

    def __str__(self):
        return "{}".format(self.name)

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
