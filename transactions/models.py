from django.db import models
from accounts.models import ClientUser, CashOutAgent, Merchant, Customer


# Create your models here.
class Payment(models.Model):
    customer = models.ForeignKey(Customer, to_field="user", on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, to_field="user", on_delete=models.CASCADE)
    amount = models.FloatField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.customer.user.first_name+"-"+self.merchant.user.first_name+":"+str(self.amount))


class MoneyTransfer(models.Model):
    sender = models.ForeignKey(Customer, to_field="user", on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(Customer, to_field="user", on_delete=models.CASCADE, related_name="receiver")
    amount = models.FloatField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.sender.user.first_name+"-"+self.receiver.user.first_name+":"+str(self.amount))


class AddMoney(models.Model):
    customer = models.ForeignKey(Customer, to_field="user", on_delete=models.CASCADE)
    card_no = models.CharField(max_length=20, null=False, blank=False)
    card_holder_name = models.CharField(max_length=50, null=False, blank=False)
    issuer_bank = models.CharField(max_length=50, null=False, blank=False)
    amount = models.FloatField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.customer.user.first_name+" "+self.customer.user.last_name+"-"+self.issuer_bank+":"+str(self.amount))


class Balance(models.Model):
    user = models.ForeignKey(ClientUser, to_field="mobile", on_delete=models.CASCADE)
    ledger_balance = models.FloatField(null=False, blank=False)
    available_balance = models.FloatField(null=False, blank=False)

    def __str__(self):
        return str(self.user+"-"+self.ledger_balance+":"+self.available_balance)


class Cashout(models.Model):
    agent = models.ForeignKey(CashOutAgent, to_field="user", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, to_field="user", on_delete=models.CASCADE)
    amount = models.FloatField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.agent.user.first_name+"-"+self.customer.user.first_name+":"+str(self.amount))


class Offer(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    details = models.CharField(max_length=200, null=False, blank=False)
    start_datetime = models.DateTimeField(blank=True)
    end_datetime = models.DateTimeField(blank=True)

    def __str__(self):
        return str(self.title)