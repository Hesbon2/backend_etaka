from phone_verify.models import SMSVerification
from rest_framework import generics
from .models import Customer, ClientUser
from .serializer import ClientUserSerializer
from rest_framework.response import Response
from rest_framework import status

class CustomerList(generics.ListCreateAPIView):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer


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
            print(mobile)
            client = ClientUser.objects.get(mobile=mobile)
            serializer = ClientUserSerializer(instance=client)
            return Response(serializer.data)
        except:
            return Response({'error': 'not found'},status= status.HTTP_404_NOT_FOUND )
