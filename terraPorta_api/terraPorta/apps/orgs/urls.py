from django.urls import path

import terraPorta.apps.orgs.api.create_org as orgs_api
import terraPorta.apps.orgs.api.update_org as update_api
import terraPorta.apps.orgs.api.invite_users as invite_api

urlpatterns = [
	path('orgs/', orgs_api.OrganizationView.as_view(), name='orgs'),
	path('orgs/<id>/', update_api.UpdateOrg.as_view(), name='get_update_delete_org'),
	path('get_orgs/', orgs_api.MemeberListOrgsView.as_view(), name='list_orgs'),
	path('invite_users/<id>/', invite_api.InviteUsers.as_view(), name='invite_users'),
	path('user_activation/<code>/', invite_api.InviteUserActivation.as_view(), name='user_activation'),
]
