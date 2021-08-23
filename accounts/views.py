from phone_verify.models import SMSVerification
from rest_framework import generics
from .models import Customer
from .serializer import CustomerSerializer
from rest_framework.response import Response


class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer

class DetailsByToken(generics.RetrieveAPIView):
    def get(self, request):
        token = self.request.headers.get('Authorization')
        print("TOKEN::", token)
        try:
            token_obj = SMSVerification.objects.get(session_token=token)
            mobile = token_obj.phone_number
            customer = Customer.objects.get(mobile=mobile)
            serializer = CustomerSerializer(instance=customer)
            return Response(serializer.data)
        except:
            return Response({'error': 'not found'})
