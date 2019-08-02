from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.events.models import Events, EventHook
from terraPorta.apps.events.resources import EventSerializer, GetEventAndSubscribed


class UpdateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        event = get_object_or_404(Events, id=id)
        subscribed_events = EventHook.objects.filter(event=event)
        data = {
            'event': event,
            'subscribed': subscribed_events
        }
        serializer = GetEventAndSubscribed(data)
        user_subs = EventHook.objects.filter(user=request.user).filter(event=event)
        if user_subs:
            serializer.data['event'].update({'user_subscribed': True})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        if request.user.is_superuser:
            event = get_object_or_404(Events, id=id)
            serializer = EventSerializer(event, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            event = get_object_or_404(Events, id=id, owner=request.user)
            event.delete()
            return Response('Event has been deleted', status=status.HTTP_200_OK)
        else:
            return Response('Is not staff or superuser', status=status.HTTP_403_FORBIDDEN)
