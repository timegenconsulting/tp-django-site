from django.shortcuts import get_list_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.events.models import EventService
from terraPorta.apps.orgs.models import Organization


class EventServiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        check_billing_status = self.check_billing_status(request.user.pk)
        if not check_billing_status:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        eventServices = get_list_or_404(EventService)
        return Response([x.name for x in eventServices], status=status.HTTP_200_OK)

    def check_billing_status(self, user_id):
        try:
            org = Organization.objects.get(owner=user_id)
            return org.is_active()
        except Exception:
            org = Organization.objects.filter(members__id=user_id)
            if org:
                return org[0].is_active()

        return True
