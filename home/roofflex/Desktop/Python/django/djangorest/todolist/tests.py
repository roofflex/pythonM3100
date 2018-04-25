from django.test import TestCase
from .models import Task

class ModelTestCase(TestCase):
    def setUp(self):
        self.task_name = "Выполнить лабораторную работу №9"
        self.task = Task(name=self.task_name)

    def test_model_can_create_task(self):
        old_count = Task.objects.count()
        self.task.save()
        new_count = Task.objects.count()
        self.assertNotEqual(old_count, new_count)
