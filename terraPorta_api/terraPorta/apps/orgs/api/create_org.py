from django.shortcuts import get_list_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.orgs.resources import OrganizationSerializer, ListOrganizationSerializer


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Get list of organizations for requsted user
        """
        if request.user.is_superuser:
            orgs = get_list_or_404(Organization)
        else:
            return Response('Only admin can access to list.', status=status.HTTP_403_FORBIDDEN)
            # orgs = get_list_or_404(Organization, owner=request.user.pk)
        serializer = ListOrganizationSerializer(orgs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MemeberListOrgsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orgs = get_list_or_404(Organization, members=request.user.pk)
        serializer = ListOrganizationSerializer(orgs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
