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
    pin = models.CharField(max_length=5, null=False, blank=False, default='1111')

    def __str__(self):
        return str(self.first_name + " " + self.last_name + "-" + str(self.mobile))


class Customer(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    balance = models.FloatField(blank=False, null=False, default=0)
    photo = models.ImageField(null=True, blank=True, upload_to='Picture/Customer/', )
    
    def __str__(self):
        return str(self.user.first_name+" "+ self.user.last_name)


class CashOutAgent(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    balance = models.FloatField(blank=False, null=False, default=0)
    photo = models.ImageField(null=True, blank=True, upload_to='Picture/Agent/', )

    def __str__(self):
        return str(self.user.first_name+" "+ self.user.last_name)

merchant_type_list = [
    ("ELEC", "Electricity", ), ("WAT", "Water"), ("GAS", "Gas"), ("EDU", "Education"), ("NET", "Internet"), ("CARD", "Credit Card"),
    ("TEL", "Telephone"), ("TV", "Television")
]
class Merchant(models.Model):
    user = models.OneToOneField(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    org_name = models.CharField(max_length=50, null=False, blank=False)
    merchant_type = models.CharField(max_length=100,choices= merchant_type_list, blank=True,null= True)
    trade_lic = models.CharField(max_length=50, null=False, blank=False)
    balance = models.FloatField(blank=False, null=False, default=0)
    photo = models.ImageField(null=True, blank=True, upload_to='Picture/Merchant/', )

    def __str__(self):
        return str(self.org_name)
