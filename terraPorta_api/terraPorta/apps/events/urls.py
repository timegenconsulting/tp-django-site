from django.urls import path

import terraPorta.apps.events.api.create_event as event
import terraPorta.apps.events.api.update_event as update
import terraPorta.apps.events.api.event_services as eventservice
import terraPorta.apps.events.api.event_hook as hook
import terraPorta.apps.events.api.update_event_hook as hook_update

urlpatterns = [
    path('eventservices/', eventservice.EventServiceView.as_view(), name='eventservices'),
    path('events/', event.CreateEventView.as_view(), name='events'),
    path('event/<id>/', update.UpdateEventView.as_view(), name='update_delete'),
    path('create_hook/<event>/', hook.CreateEventHookView.as_view(), name='hooks'),
    path('list_event_hook/<org>/', hook.ListEventHookView.as_view(), name='list_hooks'),
    path('event_hook/<org>/<event>/', hook_update.EventHookView.as_view(), name='event_hook'),
    path('test/', hook_update.TestEvent.as_view(), name='test'),
]
