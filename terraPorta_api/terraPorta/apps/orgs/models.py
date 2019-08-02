import datetime
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Organization(models.Model):
    owner = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE, null=True)
    members = models.ManyToManyField(User, blank=True, related_name="members")
    name = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=50, blank=True)
    requests_no = models.BigIntegerField(default=0)

    date_joined = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    billing_date = models.DateTimeField(null=True)

    def __str__(self):
        return 'Name: {}'.format(self.name)

    def is_active(self):
        if self.billing_date:
            if self.active and self.billing_date.isoformat() > datetime.datetime.now().isoformat():
                return True
        return False
