from django.shortcuts import render
# Create your views here.
from phone_verify.models import SMSVerification
from rest_framework import generics
from rest_framework.response import Response
from accounts.models import ClientUser, Customer
from .models import AddMoney, MoneyTransfer, Payment, Cashout, Offer
from .serializer import AddMoneySerializer, MoneyTransferSerializer, PaymentSerializer, OfferSerializer


class AddMoneyView(generics.RetrieveAPIView):

    def get(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = ClientUser.objects.get(mobile=mobile)
            add_money = AddMoney.objects.filter(customer__user=client)
            # print(add_money)
            # add_money = list(add_money)
            serializer = AddMoneySerializer(add_money, many=True, required=False)
            return Response(serializer.data)
        except:
            return Response({"error": "not found"})


class MoneyTransferView(generics.RetrieveAPIView):

    def get(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = Customer.objects.get(user__mobile=mobile)
            send_money = MoneyTransfer.objects.filter(sender=client)
            rec_money = MoneyTransfer.objects.filter(receiver=client)
            result = send_money | rec_money
            print(result)

            # add_money = list(add_money)
            serializer = MoneyTransferSerializer(result, many=True, required=False)
            return Response(serializer.data)
        except:
            return Response({"error": "not found"})


class PaymentView(generics.RetrieveAPIView):

    def get(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = Customer.objects.get(user__mobile=mobile)
            result = Payment.objects.filter(customer=client)
            print(result)
            # add_money = list(add_money)
            serializer = PaymentSerializer(result, many=True, required=False)
            return Response(serializer.data)
        except:
            return Response({"error": "not found"})


class CashOutView(generics.RetrieveAPIView):

    def get(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = Customer.objects.get(user__mobile=mobile)
            result = Cashout.objects.filter(customer=client)
            print(result)
            # add_money = list(add_money)
            serializer = PaymentSerializer(result, many=True, required=False)
            return Response(serializer.data)
        except:
            return Response({"error": "not found"})



class OfferList(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
