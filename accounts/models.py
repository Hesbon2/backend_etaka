from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    gender = models.BooleanField(default=True),
    # mobile = models.CharField(null=False, blank=False, max_length=20)# True for male and False for female
    # password = None,
    # you can add more fields here.


class Customer(models.Model):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    mobile = models.CharField(max_length=100, blank=False, null=False)
    nid = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.first_name+" "+self.last_name+"-"+self.mobile)



