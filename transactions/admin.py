from django.contrib import admin
from .models import Payment, MoneyTransfer, AddMoney, Cashout, Offer

admin.site.register(Payment)
admin.site.register(MoneyTransfer)

admin.site.register(AddMoney)
admin.site.register(Cashout)
admin.site.register(Offer)
