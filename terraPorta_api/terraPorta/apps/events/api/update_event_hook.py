from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from terraPorta.apps.events.models import EventHook
from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.events.resources import HookSerializer


class EventHookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org, event):
        get_hook = get_object_or_404(EventHook, org=org, event=event)
        serializer = HookSerializer(get_hook)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, org, event):
        try:
            hook = get_object_or_404(EventHook, org=org, event=event)
            serializer = HookSerializer(hook, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response('User is not the owner', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, org, event):
        try:
            Organization.objects.get(owner=request.user)
            get_hook = get_object_or_404(EventHook, org=org, event=event)
            deleted_hook = get_hook.event
            get_hook.delete()
            return Response('Event Hook "{}" has been deleted'.format(deleted_hook), status=status.HTTP_200_OK)
        except Exception:
            return Response('User is not the owner', status=status.HTTP_403_FORBIDDEN)


class TestEvent(APIView):
    permission_classes = []

    def post(self, request):
        print(request)
        # print(request.data)
        return Response("worked", status=status.HTTP_200_OK)
