import jwt

from django.shortcuts import get_list_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.events.models import Events, EventHook
from terraPorta.apps.events.resources import ListEventsSerializer, CreateEventsSerializer

from terraPorta.apps.orgs.models import Organization


class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        check_billing_status = self.check_billing_status(request.user.pk)
        if not check_billing_status:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        events = get_list_or_404(Events)
        if request.user.is_superuser:
            subscribed_events = EventHook.objects.all()
        else:
            subscribed_events = EventHook.objects.filter(user=request.user.pk)
        data = {
            'events': events,
            'subscribed': subscribed_events
        }
        serializer = ListEventsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            request_data = request.data
            request_data['owner'] = request.user.pk
            serializer = CreateEventsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)

    def check_billing_status(self, user_id):
        try:
            org = Organization.objects.get(owner=user_id)
            return org.is_active()
        except:
            org = Organization.objects.filter(members__id=user_id)
            if org:
                return org[0].is_active()

        return True

