import uuid
from django_filters import rest_framework as filters
from accounts.serializer import CustomerSerializer
from django.shortcuts import render
# Create your views here.
from phone_verify.models import SMSVerification
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import CashOutAgent, ClientUser, Customer, Merchant
from .models import AddMoney, History, MoneyTransfer, Payment, Cashout, Offer
from .serializer import AddMoneySerializer, HistorySerializer, MoneyTransferSerializer, PaymentSerializer, OfferSerializer


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
        #try:
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
        trn_id = uuid.uuid4().hex[:10].upper()
        history = History(amount=request.data['amount'], user= client, trans_type="ADDMONEY", trans_id=trn_id)
        history.save()
        customer.balance = customer.balance + add_money.amount
        customer.save()
        data = {"status": "success",
                "tran_id" : trn_id
                }
        return Response(data)
        # except:
        #     return Response({"status": "failed"})


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


class CashOutView(APIView):

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


    def post(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            print(request.data['cashout_agent'])
            client = Customer.objects.get(user__mobile=mobile)
            print(client)
            agent = CashOutAgent.objects.get(user__mobile=request.data['cashout_agent'])
            print(agent)
            print(request.data['cashout_amount'])
            obj = Cashout(agent=agent, customer=client, amount=request.data['cashout_amount'])
            obj.save()
            client.balance = client.balance - request.data['cashout_amount']
            agent.balance = agent.balance + request.data['cashout_amount']
            client.save()
            agent.save()
            # add_money = list(add_money)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "failed to cashout"}, status=status.HTTP_400_BAD_REQUEST)


class OfferList(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('location',)

class BillPaymentView(APIView):

    # def get(self, request):
    #     # global serializer
    #     token = self.request.headers.get('Authorization')
    #     print("TOKEN::", token)
    #     try:
    #         token_obj = SMSVerification.objects.get(session_token=token)
    #         mobile = token_obj.phone_number
    #         client = Customer.objects.get(user__mobile=mobile)
    #         result = Cashout.objects.filter(customer=client)
    #         print(result)
    #         # add_money = list(add_money)
    #         serializer = PaymentSerializer(result, many=True, required=False)
    #         return Response(serializer.data)
    #     except:
    #         return Response({"error": "not found"})


    def post(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            print(mobile)
            print(request.data['merchant_id'])
            client = Customer.objects.get(user__mobile=mobile)
            print(client)
            merchant = Merchant.objects.get(id=request.data['merchant_id'])
            print(merchant)
            print(request.data['bill_amount'])
            obj = Payment(merchant=merchant, customer=client, amount=request.data['bill_amount'],reference=request.data['reference'])
            obj.save()
            client.balance = client.balance - request.data['bill_amount']
            merchant.balance = merchant.balance + request.data['bill_amount']
            client.save()
            merchant.save()
            # add_money = list(add_money)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "failed to payment"}, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistory(APIView):
    def get(self, request):
        # global serializer
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            client = ClientUser.objects.get(mobile=mobile)
            tran_history = History.objects.filter(customer__user=client)
            # print(add_money)
            # add_money = list(add_money)
            serializer = HistorySerializer(tran_history, many=True, required=False)
            return Response(serializer.data)
        except:
            return Response({"error": "not found"})