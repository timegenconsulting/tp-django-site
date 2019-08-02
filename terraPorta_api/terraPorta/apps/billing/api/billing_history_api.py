
from django.shortcuts import get_list_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.billing.models import Payment
from terraPorta.apps.billing.resources import BillingHistorySerializer


class BillingHistoryApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payment = get_list_or_404(Payment)
        serializer = BillingHistorySerializer(payment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
