import jwt

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.accounts.resources import GetUserSerializer, CreateUserSerializer
import terraPorta.apps.accounts.utilities as utilities
import terraPorta.apps.orgs.tasks as tasks


class InviteUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        org = get_object_or_404(Organization, id=id)
        if request.user.is_superuser or org.owner == request.user:
            get_users = User.objects.all()
            serializer = GetUserSerializer(get_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response('User is not the owner or admin', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, id):
        email = request.data.get('email')

        if email:
            # use small caps only
            email = email.lower()
            org = get_object_or_404(Organization, id=id)
            if request.user.is_superuser or org.owner == request.user:
                try:
                    user = User.objects.get(email=email)
                    if Organization.objects.filter(owner=user.id):
                        return Response('The owner of an organization can not be invited', status=status.HTTP_400_BAD_REQUEST)

                    if Organization.objects.filter(members__id=user.id):
                        return Response('The user is already a member of another organization', status=status.HTTP_400_BAD_REQUEST)

                    code = utilities.generate_invite_code(email, org.id)
                    tasks.UserInvitation().run(
                        user.email,
                        str(code),
                        org.name,
                        user.username
                    )
                except:
                    code = utilities.generate_invite_code(email, org.id)
                    tasks.UserInvitation().run(
                        email,
                        str(code),
                        org.name
                    )
                return Response('Invitation was sent', status=status.HTTP_201_CREATED)

            else:
                return Response('User is not the owner or admin', status=status.HTTP_403_FORBIDDEN)

        return Response("Missing email", status=status.HTTP_400_BAD_REQUEST)


class InviteUserActivation(APIView):
    permission_classes = []

    def get(self, request, code):
        try:
            check_code = jwt.decode(str.encode(code), "terraportainviteusers!", algorithms=["HS256"])
            try:
                User.objects.get(email=check_code['email'])
                return Response(True, status=status.HTTP_200_OK)
            except:
                return Response(False, status=status.HTTP_200_OK)
        except:
            return Response("Invitation key invalid or expired", status=status.HTTP_403_FORBIDDEN)

    def put(self, request, code):
        try:
            check_code = jwt.decode(str.encode(code), "terraportainviteusers!", algorithms=["HS256"])
            org = get_object_or_404(Organization, id=check_code['org'])
            try:
                user = User.objects.get(email=check_code['email'])
                if Organization.objects.filter(id=check_code['org']).filter(members__id=user.id):
                    return Response("User has been added to the organization.", status=status.HTTP_200_OK)
                org.members.add(user)
                org.save()
                return Response('User has been added to the organization.', status=status.HTTP_200_OK)
            except:
                request_data = request.data
                request_data['is_active'] = True
                request_data['email'] = check_code['email']
                # if request.data['email'] and request.data['email'] == check_code['email']:
                serializer = CreateUserSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    org.members.add(user)
                    org.save()
                    return Response('The user is registered and added to the organization', status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     return Response("Invitation email does not match with email sent for registration", status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Invitation key invalid or expired", status=status.HTTP_403_FORBIDDEN)
