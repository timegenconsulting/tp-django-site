import datetime
import jwt
import uuid
import warnings

from calendar import timegm

from rest_framework_jwt.compat import get_username
from rest_framework_jwt.compat import get_username_field
from rest_framework_jwt.settings import api_settings

from terraPorta.apps.orgs.models import Organization

def generate_recovery_code(email):
    reset_key = jwt.encode(
        {
            "key": email,
            "exp": datetime.datetime.now()+datetime.timedelta(days=2)
        }, "terraportaressetpassword!", algorithm="HS256").decode('utf-8')
    return reset_key

def generate_activation_code(username):
    activation_key = jwt.encode(
        {
            "key": username,
            "exp": datetime.datetime.now()+datetime.timedelta(days=10)
        }, "terraportaactivationcode!", algorithm="HS256").decode('utf-8')
    return activation_key

def generate_invite_code(email, org_id):
    activation_key = jwt.encode(
        {
            "email": email,
            "org": org_id,
            "exp": datetime.datetime.now()+datetime.timedelta(days=2)
        }, "terraportainviteusers!", algorithm="HS256").decode('utf-8')
    return activation_key

def jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)
    try:
        org = Organization.objects.get(owner=user.pk)
        is_owner = True
        org_active = org.active
        org_billing_active = org.is_active()
        org_id = org.id
    except:
        org = Organization.objects.filter(members__id=user.pk)
        if org:
            is_owner = False
            org_id = org[0].id
            org_billing_active = org[0].is_active()
            org_active = org[0].active
        else:
            is_owner = False
            org_id = None
            org_billing_active = False
            org_active = False

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    payload = {
        'user_id': user.pk,
        'username': username,
        'is_superuser': user.is_superuser,
        'is_owner': is_owner,
        'org_id': org_id,
        'org_active': org_active,
        'org_billing_active': org_billing_active,
        'exp': datetime.datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr(user, 'email'):
        payload['email'] = user.email
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload
