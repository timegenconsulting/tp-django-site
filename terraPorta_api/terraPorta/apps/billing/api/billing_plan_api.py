from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.billing.models import BillingPlan, Provider
from terraPorta.apps.billing.resources import ListBillingPlanSerializer, BillingPlanSerializer, GetBillingPlanSerializer



class GetProvidersApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        providers = get_list_or_404(Provider)
        return Response([x.name for x in providers], status=status.HTTP_200_OK)


class BillingPlansApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = get_list_or_404(BillingPlan)
        serializer = ListBillingPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            serializer = BillingPlanSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)


class BillingPlanUpdateDeleteApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        plan = get_object_or_404(BillingPlan, id=id)
        serializer = GetBillingPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        if request.user.is_superuser:
            plan = get_object_or_404(BillingPlan, id=id)
            request_data = request.data
            request_data['price'] = request_data['price'] * 100
            serializer = GetBillingPlanSerializer(plan, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            plan = get_object_or_404(BillingPlan, id=id)
            plan.delete()
            return Response('Plan has been deleted', status=status.HTTP_200_OK)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)

