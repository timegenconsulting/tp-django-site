import jwt
from datetime import datetime
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.orgs.resources import OrgSerializer

from terraPorta.apps.billing.models import Payment
from terraPorta.apps.billing.resources import BillingHistorySerializer


class UpdateOrg(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        org = get_object_or_404(Organization, id=id)
        serializer = OrgSerializer(org, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        if request.user.is_superuser:
            get_org = get_object_or_404(Organization, id=id)
        else:
            get_org = get_object_or_404(Organization, id=id, owner=request.user.pk)

        billing_history = Payment.objects.filter(org=id)
        billing_serializer = BillingHistorySerializer(billing_history, many=True)

        if get_org.billing_date:
            left_days = get_org.billing_date.strftime('%m-%d-%Y %H:%M:%S')
        else:
            left_days = "-"

        members = get_org.members.all()
        members_list = []
        for mem in members:
            members_list.append(
                {
                    'id': mem.id,
                    'username': mem.username,
                    'email': mem.email,
                    'first_name': mem.first_name,
                    'last_name': mem.last_name
                }
            )
        serializer = OrgSerializer(get_org, many=False)

        ser_data = serializer.data
        ser_data['owner_name'] = get_org.owner.username
        ser_data['members_list'] = members_list
        ser_data['left_days'] = left_days
        ser_data['billing_is_active'] = get_org.is_active()
        ser_data['billing_history'] = billing_serializer.data
        return Response(ser_data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        org = get_object_or_404(Organization, id=id)
        org.active = False
        org.save()
        return Response('Organization has been deleted', status=status.HTTP_200_OK)
