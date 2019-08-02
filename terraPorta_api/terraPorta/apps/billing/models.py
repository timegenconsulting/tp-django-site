from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from terraPorta.apps.orgs.models import Organization


class Provider(models.Model):
    name = models.CharField(max_length=500, primary_key=True, unique=True)


class Payment(models.Model):
    org = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    user = models.CharField(max_length=191)
    amount = models.IntegerField()
    transaction_id = models.CharField(unique=True, max_length=250, blank=True)
    balance_transaction = models.CharField(blank=True, max_length=250)
    order_id = models.CharField(max_length=250, unique=True)
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=250, blank=True)
    full_response = JSONField(blank=True, null=True)
    failure_code = models.CharField(max_length=50, blank=True, null=True)
    failure_message = models.CharField(max_length=250, blank=True, null=True)
    provider = models.CharField(max_length=250, blank=True, null=True)


class BillingPlan(models.Model):
    days = models.IntegerField()
    description = models.CharField(max_length=250, default="One month")
    price = models.FloatField(default=0)
    provider = models.ForeignKey(Provider, null=True, on_delete=models.SET_NULL)
