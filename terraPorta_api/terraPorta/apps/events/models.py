from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from terraPorta.apps.orgs.models import Organization
from django.contrib.auth.models import User

EVENT_HOOK_TYPE = (
        ('url', 'url'),
        ('email', 'email'),
    )


class EventService(models.Model):
    name = models.CharField(max_length=500, primary_key=True, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Events(models.Model):
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    event = models.CharField(max_length=500)
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    service = models.ForeignKey(EventService, null=True, on_delete=models.SET_NULL)

    body = JSONField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.event)


class EventHook(models.Model):
    event = models.ForeignKey(Events, related_name="event_url", on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, related_name="organization", null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, related_name="user", null=True, on_delete=models.SET_NULL)
    hook_link = models.CharField(max_length=500)
    hook_type = models.CharField(max_length=6, choices=EVENT_HOOK_TYPE, default='url')
    body = JSONField(blank=True, null=True)
