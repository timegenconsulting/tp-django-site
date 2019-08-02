import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import terraPorta.apps.accounts.tasks as tasks

logger = logging.getLogger("terraPorta.api")


class RecoveryUsernameView(APIView):
    permission_classes = []

    def post(self, request):
        """
        Send username to user.
        """

        email = request.data.get('email')
        if email:
            # use small caps only
            email = email.lower()

            user = get_object_or_404(get_user_model(), email=email,
                                     is_active=True)

            # send email
            tasks.UsernameRecovery().run(
                user.username,
                user.email
            )
            return Response('Email was successfully sent', status=status.HTTP_200_OK)

        # invalid data submitted
        return Response("Missing email", status=status.HTTP_400_BAD_REQUEST)
