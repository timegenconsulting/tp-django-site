from django.urls import path
import terraPorta.apps.accounts.api.create_user as users_api
import terraPorta.apps.accounts.api.passwords as pass_api
import terraPorta.apps.accounts.api.username_recovery as recovery_api
import terraPorta.apps.accounts.api.profile as profile_api

from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('token/', obtain_jwt_token, name='login'),
    path('users/', users_api.UserCreate.as_view(), name='users'),
    path('users/password/', pass_api.ChangePasswordView.as_view(), name='change_password'),
    path('users/profile/', profile_api.UpdateProfile.as_view(), name='profile'),
    path('users/<id>/', users_api.GetUserView.as_view(), name='user_detail'),
    path('password_recovery/<code>/', pass_api.RecoveryPasswordView.as_view(), name='password_recovery'),
    path('password_recovery/', pass_api.RecoveryPasswordView.as_view(), name='password_recovery_request'),
    path('username_recovery/', recovery_api.RecoveryUsernameView.as_view(), name='username_recovery'),
    path('activation/<code>/', users_api.UserActivationView.as_view(), name='activation'),
    path('user_deactivation/<id>/', users_api.UserDeactivationView.as_view(), name='user_deactivation'),
]
