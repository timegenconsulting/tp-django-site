import jwt
import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.accounts.resources import PasswordSerializer, PasswordResetSerializer
import terraPorta.apps.accounts.utilities as utilities
import terraPorta.apps.accounts.tasks as tasks

logger = logging.getLogger("terraPorta.api")


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        Change password
        """
        user = request.user

        current_password = request.data.get('current_password')
        serializer = PasswordSerializer(data=request.data)

        # perform password update if everything is ok
        if serializer.is_valid() and user.check_password(current_password):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response("Password changed succesfully", status=status.HTTP_200_OK)

        # invalid data submitted
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecoveryPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        """
        Send recovery password code
        """

        email = request.data.get('email')
        if email:
            # use small caps only
            email = email.lower()

            user = get_object_or_404(get_user_model(), email=email,
                                     is_active=True)
            # create recovery code
            code = utilities.generate_recovery_code(email)
            # cache.set('recovery_code', str(code))
            tasks.PasswordRecovery().run(
                user.username,
                user.email,
                str(code)
            )
            return Response({'recovery_key': str(code)}, status=status.HTTP_200_OK)

        # invalid data submitted
        return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, code):

        check_recovery = jwt.decode(str.encode(code), "terraportaressetpassword!", algorithms=["HS256"])

        user = User.objects.get(email=check_recovery['key'])

        new_password = request.data.get('new_password')
        repeated_password = request.data.get('repeated_password')

        data = {
            'new_password': new_password,
            'repeated_password': repeated_password,
            'current_password': user.password
        }
        # performs data validity check
        serializer = PasswordResetSerializer(data=data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            print(user.check_password(new_password))
            return Response('Password changed successfully', status=status.HTTP_200_OK)
        # invalid data submitted
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
