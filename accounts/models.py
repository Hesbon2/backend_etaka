from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   gender = models.BooleanField(default=True) ,
   # mobile = models.CharField(null=False, blank=False, max_length=20)# True for male and False for female
   # password = None,
   # you can add more fields here.