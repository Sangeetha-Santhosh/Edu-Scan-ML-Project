from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_TEACHER = 'TEACHER'
    ROLE_STUDENT = 'STUDENT'
    ROLE_CHOICES = (
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    def is_student(self):
        return self.role == self.ROLE_STUDENT
