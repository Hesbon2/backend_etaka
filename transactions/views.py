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
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError, DatabaseError



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
            trn_id = uuid.uuid4().hex[:10].upper()

            # Get description from request, use default if not provided
            description = request.data.get('description', 'Mps deposit through mobile')

            # Get optional sender details
            beneficiary = request.data.get('beneficiary') or None
            trans_mode = request.data.get('trans_mode') or None
            bank_name = request.data.get('bank_name') or None

            customer.balance = customer.balance + add_money.amount
            history = History(
                amount=request.data['amount'],
                user=client,
                description=description,
                bal=customer.balance,
                trans_type="Credit",
                trans_id=trn_id,
                # Add the new optional fields
                beneficiary=beneficiary,
                trans_mode=trans_mode,
                bank_name=bank_name
            )
            history.save()
            customer.save()
            data = {"status": "success",
                    "tran_id" : trn_id
                    }
            return Response(data)
        except Exception as e:
            print(f"AddMoney error: {e}")
            return Response({"status": "failed", "error": str(e)})


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

        # 1) Auth → sender
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
        except SMSVerification.DoesNotExist:
            return Response({"error": "invalid_token"}, status=status.HTTP_401_UNAUTHORIZED)

        mobile = token_obj.phone_number
        try:
            sender = Customer.objects.select_for_update().get(user__mobile=mobile)
        except Customer.DoesNotExist:
            return Response({"error": "sender_not_found"}, status=status.HTTP_404_NOT_FOUND)

        # 2) Receiver normalization and lookup (accept with or without '+')
        recv_raw = str(request.data.get('receiver', '')).strip()
        recv_num = recv_raw.lstrip('+')
        receiver = (
            Customer.objects.select_for_update().filter(user__mobile=recv_num).first()
            or Customer.objects.select_for_update().filter(user__mobile='+' + recv_num).first()
        )
        if receiver is None:
            return Response({"error": "receiver_not_found"}, status=status.HTTP_404_NOT_FOUND)

        # 3) Amount parse/validate
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "amount_invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "amount_must_be_positive"}, status=status.HTTP_400_BAD_REQUEST)
        if sender == receiver:
            return Response({"error": "cannot_send_to_self"}, status=status.HTTP_400_BAD_REQUEST)

        s_bal = Decimal(str(sender.balance))
        r_bal = Decimal(str(receiver.balance))
        if s_bal < amount:
            return Response({"error": "insufficient_funds"}, status=status.HTTP_400_BAD_REQUEST)

        # 4) Optional fields (safe defaults to satisfy NOT NULL / NULLable constraints)
        description = request.data.get('description', '')
        beneficiary = request.data.get('beneficiary') or None
        trans_mode = request.data.get('trans_mode') or None
        ben_account = request.data.get('ben_account') or None

        # NEW: Add the two new optional fields
        bank_name = request.data.get('bank_name') or None
        branch_code = request.data.get('branch_code') or None

        # 5) Perform transfer atomically
        try:
            with transaction.atomic():
                # Create money transfer record
                MoneyTransfer.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=float(amount),  # your schema uses real (float); keep types consistent
                    description=description,
                    beneficiary=beneficiary,
                    trans_mode=trans_mode,
                    ben_account=ben_account,
                    # NEW: Add the two new fields
                    bank_name=bank_name,
                    branch_code=branch_code,
                )

                # Update balances
                s_bal -= amount
                r_bal += amount
                sender.balance = float(s_bal)
                receiver.balance = float(r_bal)

                # Histories (your table requires: trans_id (PK), trans_type, amount, user, description, bal)
                trn_id_send = uuid.uuid4().hex[:10].upper()
                History.objects.create(
                    trans_type="Debit",
                    trans_id=trn_id_send,
                    amount=float(amount),
                    user=sender.user,
                    description=description,
                    bal=float(s_bal),
                    beneficiary=beneficiary,
                    trans_mode=trans_mode,
                    ben_account=ben_account,
                    # NEW: Add the two new fields to history as well
                    bank_name=bank_name,
                    branch_code=branch_code,
                )

                trn_id_recv = uuid.uuid4().hex[:10].upper()
                History.objects.create(
                    trans_type="Credit",
                    trans_id=trn_id_recv,
                    amount=float(amount),
                    user=receiver.user,
                    description=description,
                    bal=float(r_bal),
                    beneficiary=beneficiary,
                    trans_mode=trans_mode,
                    ben_account=ben_account,
                    # NEW: Add the two new fields to history as well
                    bank_name=bank_name,
                    branch_code=branch_code,
                )

                sender.save(update_fields=["balance"])
                receiver.save(update_fields=["balance"])

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({"error": f"integrity_error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"error": f"db_error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"{e.__class__.__name__}: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            trn_id = uuid.uuid4().hex[:10].upper()
            history = History(amount=request.data['cashout_amount'], user= client.user, trans_type="CASHOUT", trans_id=trn_id)
            history.save()
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
            trn_id = uuid.uuid4().hex[:10].upper()
            history = History(amount=request.data['bill_amount'], user= client.user, trans_type="BILLPAY", trans_id=trn_id)
            history.save()
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
        # try:
        token_obj = SMSVerification.objects.get(session_token=token)
        mobile = token_obj.phone_number
        client = ClientUser.objects.get(mobile=mobile)
        tran_history = History.objects.filter(user=client)
        # print(add_money)
        # add_money = list(add_money)
        serializer = HistorySerializer(tran_history, many=True, required=False)
        return Response(serializer.data)
        # except:
        #     return Response({"error": "not found"})