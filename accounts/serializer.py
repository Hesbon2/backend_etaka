from phone_verify.models import SMSVerification
from rest_framework import serializers
from .models import Customer, ClientUser, Merchant, CashOutAgent


class ClientUserSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ClientUser
        fields = '__all__'

    def get_balance(self, obj):
        request = self.context
        token = request.headers.get('Authorization')
        token_obj = SMSVerification.objects.get(session_token=token)
        mobile = token_obj.phone_number
        client = ClientUser.objects.get(mobile=mobile)
        customer = Customer.objects.get(user=client)
        return customer.balance


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
