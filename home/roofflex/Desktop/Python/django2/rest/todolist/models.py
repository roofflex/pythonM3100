from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):

        return "{}".format(self.name)



class Tasklist(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey('auth.User')
    vipusers = models.ManyToManyField('auth.User',related_name='vipusers', blank= True)
    view_users = models.ManyToManyField('auth.User',related_name='view_users', blank = True)
    def __str__(self):
        return "{} {} {} {}".format(self.name,self.owner, self.vipusers, self.viewusers)


class Task(models.Model):
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    completed = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    date_modified = models.DateField(auto_now=True)
    tasklist = models.ForeignKey(Tasklist, related_name='tasks', on_delete=models.CASCADE)
    PRIORITY = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    )
    priority = models.CharField(max_length=1, choices=PRIORITY, default='n')
    tags = models.ManyToManyField(Tag)
    def __str__(self):
        return "{}".format(self.name)


