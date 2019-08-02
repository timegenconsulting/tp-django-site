from django.urls import path

import terraPorta.apps.billing.api.billing_api as api
import terraPorta.apps.billing.api.billing_plan_api as plan
import terraPorta.apps.billing.api.billing_history_api as hist

urlpatterns = [
    path('charge/', api.ChargeApi.as_view(), name='charge'),
    path('get_charge/', api.GetChargeApi.as_view(), name='get_charge'),
    path('get_providers/', plan.GetProvidersApi.as_view(), name='get_providers'),
    path('billing_plans/', plan.BillingPlansApi.as_view(), name='billing_plans'),
    path('billing_plan/<id>/', plan.BillingPlanUpdateDeleteApi.as_view(), name='billing_plan_del_update'),
    path('billing_history/', hist.BillingHistoryApi.as_view(), name='billing_history')
]
