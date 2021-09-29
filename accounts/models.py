from django.db import models
from django.contrib.auth.models import AbstractUser

gender_choices = [
    ('Male', 'Male'), ('Female', 'Female')
]


class User(AbstractUser):
    gender = models.CharField(choices=gender_choices, null=False, blank=False),
    # mobile = models.CharField(null=False, blank=False, max_length=20)# True for male and False for female
    # password = None,
    # you can add more fields here.


class ClientUser(models.Model):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    mobile = models.CharField(max_length=100, blank=False, null=False, unique=True)
    email = models.CharField(max_length=100, blank=False, null=False, unique=True)
    nid = models.CharField(max_length=20, blank=False, null=False, unique=True)

    def __str__(self):
        return str(self.first_name + " " + self.last_name + "-" + self.mobile)


class Customer(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    balance = models.FloatField(blank=False, null=False, default=0)


class CashOutAgent(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    balance = models.FloatField(blank=False, null=False, default=0)


class Merchant(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    org_name = models.CharField(max_length=50, null=False, blank=False)
    trade_lic = models.CharField(max_length=50, null=False, blank=False)
    balance = models.FloatField(blank=False, null=False, default=0)
