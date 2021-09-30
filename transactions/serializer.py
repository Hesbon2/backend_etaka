from rest_framework import serializers
from .models import AddMoney, MoneyTransfer, Payment, Cashout, Offer
from phone_verify.models import SMSVerification
from accounts.models import ClientUser
from accounts.models import Customer, Merchant, CashOutAgent
from accounts.serializer import ClientUserSerializer, CustomerSerializer, CashOutAgentSerializer, MerchantSerializer


class AddMoneySerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    # customer_id = serializers.CharField(max_length=20)

    
    
    # def get_customer(self, obj):
    #     # request = self.context.get('request')
    #     # token = request.headers.get('Authorization')
    #     # print("TOKEN::", token)
    #     # token_obj = SMSVerification.objects.get(session_token=token)
    #     # mobile = token_obj.phone_number
    #     # customer = Customer.objects.get(user__mobile=mobile)
    #     # print(mobile)
    #     # serializer = CustomerSerializer(instance=customer)
    #     self.obj.customer = 
    #     return mobile
    
    class Meta:
        model = AddMoney
        fields = '__all__'

class MoneyTransferSerializer(serializers.ModelSerializer):
    sender = CustomerSerializer(read_only=True)

    class Meta:
        model = MoneyTransfer
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    merchant = MerchantSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class CashOutSerializer(serializers.ModelSerializer):
    agent = CashOutAgentSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Cashout
        fields = '__all__'


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'
