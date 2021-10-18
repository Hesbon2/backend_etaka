from accounts.serializer import CustomerSerializer
from django.shortcuts import render
# Create your views here.
from phone_verify.models import SMSVerification
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import ClientUser, Customer
from .models import AddMoney, MoneyTransfer, Payment, Cashout, Offer
from .serializer import AddMoneySerializer, MoneyTransferSerializer, PaymentSerializer, OfferSerializer


class AddMoneyView(APIView):

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

    def post(self, request, *args, **kwargs):
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = ClientUser.objects.get(mobile=mobile)
            customer = Customer.objects.get(user=client)
            cus_serializer = CustomerSerializer(instance=customer)
            add_money = AddMoney(customer=customer, amount=request.data['amount'],
                                 issuer_bank=request.data['issuer_bank'], card_no=request.data['card_no'],
                                 card_holder_name=request.data['card_holder_name'])
            amount = request.POST.get('amount')
            print(request.data['amount'])
            add_money.save()
            customer.balance = customer.balance + add_money.amount
            customer.save()
            return Response({"status": "success"})
        except:
            return Response({"status": "failed"})


class AddMoneyCreate(generics.CreateAPIView):
    serializer = AddMoneySerializer

    def post(self, request, *args, **kwargs):
        serializer = AddMoneySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


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


class MoneyTransferCreate(generics.CreateAPIView):
    model = MoneyTransfer
    serializer_class = MoneyTransferSerializer


class SendMoney(APIView):
    def post(self, request):
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            print(mobile)
            client = Customer.objects.get(user__mobile=mobile)
            receiver = Customer.objects.get(user__mobile=request.data['receiver'])
            money_transfer = MoneyTransfer(sender=client, receiver=receiver, amount=request.data['amount'])
            money_transfer.save()
            client.balance = client.balance - request.data['amount']
            receiver.balance = receiver.balance + request.data['amount']
            client.save()
            receiver.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "failed to send"}, status=status.HTTP_400_BAD_REQUEST)


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
