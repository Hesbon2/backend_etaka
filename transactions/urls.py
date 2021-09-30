from django.contrib import admin
from django.urls import path, include
from .views import AddMoneyCreate, AddMoneyView, MoneyTransferCreate, MoneyTransferView, PaymentView, CashOutView, OfferList

urlpatterns = [
    path('addmoney/', AddMoneyView.as_view(), name='add_money'),
     path('addmoneycreate/', AddMoneyCreate.as_view(), name='add_money'),
    path('money_transfer/', MoneyTransferView.as_view(), name='money_transfer'),
    path('money_transfer_create/', MoneyTransferCreate.as_view(), name='money_transfer'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('cashout/', CashOutView.as_view(), name='cashout'),
    path('offers/', OfferList.as_view(), name='offer'),

]
