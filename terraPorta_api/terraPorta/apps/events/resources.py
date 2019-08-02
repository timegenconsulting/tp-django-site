from rest_framework import serializers

from terraPorta.apps.events.models import Events, EventHook, EventService


class ListOfEventsSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%m-%d-%Y %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Events
        fields = ('id', 'owner', 'event', 'created', 'body', 'content', 'short_description', 'service_id')


class CreateEventsSerializer(serializers.ModelSerializer):
    event = serializers.CharField(required=True)
    service_id = serializers.PrimaryKeyRelatedField(
        source='service',
        queryset=EventService.objects.all()
    )

    def create(self, validated_data):
        event = Events.objects.create(**validated_data)
        return event

    class Meta:
        model = Events
        fields = ('id', 'owner', 'event', 'created', 'body', 'content', 'short_description', 'service_id', 'service')


class EventSerializer(serializers.ModelSerializer):
    event = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(format="%m-%d-%Y %H:%M:%S", required=False, read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        source='service',
        queryset=EventService.objects.all()
    )

    class Meta:
        model = Events
        fields = ('id', 'owner', 'event', 'created', 'body', 'content', 'short_description', 'service_id', 'service')


class CreateHookSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        hook = EventHook.objects.create(**validated_data)
        return hook

    class Meta:
        model = EventHook
        fields = ('id', 'event', 'org', 'user', 'hook_link', 'hook_type', 'body')


class ListHookSerializer(serializers.ModelSerializer):
    event = serializers.ReadOnlyField(source='event.event')
    org = serializers.ReadOnlyField(source='org.name')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = EventHook
        fields = ('id', 'event', 'org', 'user', 'hook_link', 'hook_type', 'body')


class HookSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventHook
        fields = ('id', 'event', 'org', 'user', 'hook_link', 'hook_type', 'body')


class ListEventsSerializer(serializers.Serializer):
    subscribed = ListHookSerializer(many=True)
    events = ListOfEventsSerializer(many=True)


class GetEventAndSubscribed(serializers.Serializer):
    event = EventSerializer(many=False)
    subscribed = ListHookSerializer(many=True)
