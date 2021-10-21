from django.contrib import admin
from django.urls import path, include
from .views import CustomerList, DetailsByToken, CustomerRegister, MerchantList

urlpatterns = [
    path('customers/', CustomerList.as_view(), name='customers'),
    path('merchants/', MerchantList.as_view(), name='merchants'),
    path('details/', DetailsByToken.as_view(), name='details'),
    path('customer_register/', CustomerRegister.as_view(), name='register'),
]
