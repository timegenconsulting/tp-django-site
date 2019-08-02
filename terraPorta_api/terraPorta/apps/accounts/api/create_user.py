import jwt

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.accounts.resources import UserSerializer, GetUserSerializer
import terraPorta.apps.accounts.utilities as utilities
import terraPorta.apps.accounts.tasks as tasks


class UserCreate(APIView):
    """
    Creates the user.
    """
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # create activation code
                code = utilities.generate_activation_code(user.username)
                tasks.UserActivation().run(
                    user.username,
                    user.email,
                    str(code)
                )
                return Response({'key': str(code)}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.is_authenticated:
            serializer = GetUserSerializer(request.user, many=False, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        if request.user.is_authenticated:
            serializer = GetUserSerializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class GetUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = GetUserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActivationView(APIView):
    """
    Activate user
    """
    permission_classes = []

    def put(self, request, code):
        try:
            check_code = jwt.decode(str.encode(code), "terraportaactivationcode!", algorithms=["HS256"])
            user = User.objects.get(username=check_code['key'])
            if user:
                if user.is_active:
                    return Response("Account has already been activated", status=status.HTTP_200_OK)

                user.is_active = True
                user.save()
                return Response("Account has been successfully activate", status=status.HTTP_200_OK)
        except:
            return Response("Activation key invalid or expired", status=status.HTTP_403_FORBIDDEN)


class UserDeactivationView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        user = get_object_or_404(User, id=id, is_active=True)
        user.is_active = False
        user.save()
        return Response('User is deactivated', status=status.HTTP_200_OK)
