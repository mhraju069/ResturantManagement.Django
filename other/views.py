from rest_framework import viewsets,generics,status
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated



class FeedBackListCreate(generics.ListCreateAPIView):
    queryset = FeedBack.objects.filter(is_active=True)
    serializer_class = FeedBackSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}



class ContactInfoListCreate(generics.ListAPIView):
    queryset = ContactInfo.objects.filter(is_active=True)
    serializer_class = ContactInfoSerializer
    permission_classes = [AllowAny]



class SupportMessageListCreate(generics.CreateAPIView):
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    permission_classes = [AllowAny]



class AddLikeToFeedback(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedBackSerializer

    def post(self, request,feedback_id):
        try:
            feedback = FeedBack.objects.get(id=feedback_id)
        except FeedBack.DoesNotExist:
            return Response({"message": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if feedback.likes.filter(id=request.user.id).exists():
            feedback.likes.remove(request.user)
            return Response({"message": "Unlike successfully", "likes" : feedback.likes.count()}, status=status.HTTP_200_OK)
        feedback.likes.add(request.user)
        return Response({"message": "Like successfully", "likes" : feedback.likes.count()}, status=status.HTTP_200_OK)




class SubscribeNewsLetterListCreate(generics.ListCreateAPIView):
    queryset = SubscribeNewsLetter.objects.filter(is_active=True)
    serializer_class = SubscribeNewsLetterSerializer
    permission_classes = [AllowAny]
