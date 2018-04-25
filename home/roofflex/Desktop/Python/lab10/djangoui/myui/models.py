from __future__ import unicode_literals
from django.db import models
import datetime
class UserProfile(models.Model):
    user = models.CharField(max_length=40)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.date.today())
    def __str__(self):
        return self.user
    class Meta:
        verbose_name_plural=u'User profiles'
