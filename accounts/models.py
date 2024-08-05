from django.contrib.auth.models import AbstractUser,  BaseUserManager
from django.db import models



class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'client'),
        ('clientAdmin', 'clientAdmin'),
        ('admin', 'admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def is_admin(self):
        return self.user_type == 'admin'

    def __str__(self):
        return self.username
