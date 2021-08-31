from rest_framework import serializers
from .models import Customer, ClientUser, Merchant, CashOutAgent


class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'


class CashOutAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashOutAgent
        fields = '__all__'
