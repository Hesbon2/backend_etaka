from django.contrib import admin
from django.urls import path, include
from .views import CustomerList, DetailsByToken

urlpatterns = [
    path('customers/', CustomerList.as_view(), name='customers'),
    path('details/', DetailsByToken.as_view(), name='details'),
]
