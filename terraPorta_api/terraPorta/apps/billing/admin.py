from django.contrib import admin

from terraPorta.apps.billing.models import Payment, BillingPlan, Provider

admin.site.register(Payment)
admin.site.register(BillingPlan)
admin.site.register(Provider)
