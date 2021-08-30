from django.contrib import admin
from .models import User, Customer, ClientUser, CashOutAgent, Merchant

admin.site.register(User)
admin.site.register(ClientUser)
admin.site.register(Customer)
admin.site.register(CashOutAgent)
admin.site.register(Merchant)
