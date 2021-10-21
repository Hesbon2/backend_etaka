from phone_verify.models import SMSVerification
from rest_framework import generics
from rest_framework.views import APIView
from .models import Customer, ClientUser, Merchant
from .serializer import ClientUserSerializer, MerchantSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
class CustomerList(generics.ListCreateAPIView):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer
    


# class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer


class MerchantList(generics.ListCreateAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('merchant_type',)

class DetailsByToken(APIView):
    def get(self, request):
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            print(mobile)
            client = ClientUser.objects.get(mobile=mobile)
            print(client)
            serializer = ClientUserSerializer(instance=client, context=request)
            return Response(serializer.data)
        except:
            return Response({'error': 'not found'},status= status.HTTP_404_NOT_FOUND )


class CustomerRegister(APIView):
    def post(self, request):
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            print(mobile)
            client = ClientUser(mobile=mobile, first_name=request.data['first_name'], last_name=request.data['last_name'], 
            email = request.data['email'], nid=request.data['nid'], pin = request.data['pin'])
            # client.save()
            # print(client)
            # customer = Customer(user=client)
            # customer.save()
            data = {
                "mobile" : str(mobile),
                "nid" : request.data['nid'],
                "first_name" : request.data['first_name'],
                "last_name" : request.data['last_name'],
                "pin" : request.data['pin'],
                "email" : request.data['email'],
            }
            serializer = ClientUserSerializer(data=data)
            if serializer.is_valid():
                client= serializer.save()
                customer = Customer(user=client)
                customer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_302_FOUND)
        except:
            return Response({"error": "failed to register"})