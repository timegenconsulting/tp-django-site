from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.accounts.resources import ProfileSerializer, GetUserProfileSerializer


class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetUserProfileSerializer(
            {
                'user': request.user,
                'profile': request.user.profile
            }, many=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Updates user profile information.
        """
        request_data = request.data
        request_data['user'] = request.user.pk
        serializer = ProfileSerializer(request.user.profile, data=request.data)
        if serializer.is_valid():
            user = User.objects.get(id=request.user.pk)
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.email = request.data['email']
            user.save()
            serializer.save()
            return Response(request.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
