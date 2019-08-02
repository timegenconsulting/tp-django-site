from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.events.models import Events, EventHook
# from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.events.resources import ListOfEventsSerializer, CreateHookSerializer, ListHookSerializer


class CreateEventHookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event):
        events = get_list_or_404(Events)
        serializer = ListOfEventsSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, event):
        """Subscribe"""
        try:
            request_data = request.data
            request_data['event'] = event
            request_data['user'] = request.user.pk
            serializer = CreateHookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event):
        """Unsubscribe"""
        try:
            find_event_hook = get_object_or_404(EventHook, id=event, user=request.user)
            find_event_hook.delete()
            return Response('Unsubscribed', status=status.HTTP_200_OK)
        except Exception:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)


class ListEventHookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org):
        list_hook = get_list_or_404(EventHook, org=org)
        serializer = ListHookSerializer(list_hook, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
