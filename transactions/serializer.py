from rest_framework import serializers
from .models import AddMoney, History, MoneyTransfer, Payment, Cashout, Offer
from phone_verify.models import SMSVerification
from accounts.models import ClientUser
from accounts.models import Customer, Merchant, CashOutAgent
from accounts.serializer import ClientUserSerializer, CustomerSerializer, CashOutAgentSerializer, MerchantSerializer


class AddMoneySerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

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


class HistorySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username')

    class Meta:
        model = History
        fields = '__all__'

    def get_username(self, obj):
        user_name = ClientUser.objects.get(id=obj.user.id).mobile
        return user_name