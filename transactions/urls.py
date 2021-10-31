from django.urls import path
from django.urls import path

from .views import AddMoneyCreate, AddMoneyView, BillPaymentView, MoneyTransferCreate, MoneyTransferView, PaymentView, CashOutView, \
    OfferList, SendMoney, TransactionHistory

urlpatterns = [
    path('addmoney/', AddMoneyView.as_view(), name='add_money'),
     path('addmoneycreate/', AddMoneyCreate.as_view(), name='add_money'),
    path('money_transfer/', MoneyTransferView.as_view(), name='money_transfer'),
    path('sendmoney/', SendMoney.as_view(), name='money_transfer'),
    path('money_transfer_create/', MoneyTransferCreate.as_view(), name='money_transfer'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('cashout/', CashOutView.as_view(), name='cashout'),
    path('bill-payment/', BillPaymentView.as_view(), name='bill_pay'),
    path('offers/', OfferList.as_view(), name='offer'),
    path('history/', TransactionHistory.as_view(), name='history'),

]
