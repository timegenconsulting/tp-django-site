import stripe
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.billing.models import BillingPlan
from terraPorta.apps.billing.resources import CreatePaymentSerializer, RequestPaymentSerializer, ListBillingPlanSerializer
import logging
import requests


logger = logging.getLogger(__name__)


class ChargeApi(APIView):
    permission_classes = [IsAuthenticated]
    stripe.api_key = settings.STRYPE_SECRET_KEY

    def post(self, request):
        logger.info("entered {}".format(request.data))
        try:
            amount = int(request.data['amount'])
            order_id = str(uuid.uuid1())[0:8]
            user = request.user.username
            provider = request.data.get('provider', '')
            if "Stripe" in provider:
                request_data = {
                    'amount': amount,
                    'user': user,
                    'order_id': order_id
                }
                serializer = RequestPaymentSerializer(data=request_data)
                if serializer.is_valid():
                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        source=request.data['stripeToken'],
                        receipt_email=request.user.email,
                        metadata={'order_id': order_id}
                    )
                    if order_id == charge['metadata']['order_id']:
                        response_data = {
                            'transaction_id': charge['id'],
                            'balance_transaction': charge['balance_transaction'],
                            'created': datetime.fromtimestamp(charge['created']).strftime("%m/%d/%Y %H:%M:%S"),
                            'status': charge['status'],
                            'full_response': charge,
                            'failure_code': charge['failure_code'],
                            'failure_message': charge['failure_message'],
                            'org': request.data['org_id'],
                            'provider': provider
                        }
                        request_data.update(response_data)

                        serializer = CreatePaymentSerializer(data=request_data)
                        if serializer.is_valid():
                            serializer.save()
                            try:
                                expire_days = request.data['days']
                                org = get_object_or_404(Organization, id=request.data['org_id'])
                                if org.is_active():
                                    expire_date = org.billing_date + timedelta(days=int(expire_days))
                                else:
                                    expire_date = datetime.now()+timedelta(days=int(expire_days))
                            except Exception as e:
                                logger.exception('Error {}'.format(str(e)))
                                return Response('Something went wrong.', status=status.HTTP_400_BAD_REQUEST)

                            org.billing_date = expire_date
                            org.save()

                            # create new token
                            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                            payload = jwt_payload_handler(request.user)
                            token = jwt_encode_handler(payload)

                            return Response(token, status=status.HTTP_200_OK)

                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif 'IOTA' in provider:
                logger.info("IOTA payment {}".format(request.data))
                iota_payment = request.data['payment_data']
                if "ok" in iota_payment.get("recipient", {}).get('status', ''):
                    recipient = iota_payment.get("recipient", {})
                    verified_data = {}
                    try:
                        response = requests.post(
                            settings.IOTA_LOGIN,
                            auth=(
                                settings.IOTA_USER,
                                settings.IOTA_PASSWORD
                            ),
                            headers={
                                "Content-Type": "application/json",
                            }
                        )
                        response = requests.get(
                            settings.IOTA_VERIFY_URL + "" + recipient.get('id', ''),
                            headers={
                                "Authorization": response.json()['tokenId'],
                                "Content-Type": "application/json"
                            }
                        )
                        verified_data = response.json()
                        print("verified data {}".format(verified_data))
                    except Exception as e:
                        logger.exception("Iota payment verification failed: {}".format(str(e)))
                    if verified_data.get("id", None):
                        request_data = {
                            'amount': amount,
                            'user': user,
                            'order_id': order_id,
                            'transaction_id': recipient.get('id', ''),
                            'created': datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                            'status': "ok",
                            'full_response': {
                                "user_response": iota_payment,
                                "veirified_payment": verified_data,
                            },
                            'org': request.data['org_id'],
                            'provider': provider
                        }
                        serializer = CreatePaymentSerializer(data=request_data)
                        if serializer.is_valid():
                            serializer.save()
                            try:
                                expire_days = request.data['days']
                                org = get_object_or_404(Organization, id=request.data['org_id'])
                                if org.is_active():
                                    expire_date = org.billing_date + timedelta(days=int(expire_days))
                                else:
                                    expire_date = datetime.now()+timedelta(days=int(expire_days))
                            except Exception as e:
                                logger.exception('Error {}'.format(str(e)))
                                return Response('Something went wrong.', status=status.HTTP_400_BAD_REQUEST)

                            org.billing_date = expire_date
                            org.save()

                            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                            payload = jwt_payload_handler(request.user)
                            token = jwt_encode_handler(payload)
                            return Response(token, status=status.HTTP_200_OK)
                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response("payment failed", status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("payment failed", status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response('Unsuported provider.', status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception('Error {}'.format(str(e)))
            return Response('Something went wrong.', status=status.HTTP_400_BAD_REQUEST)


class GetChargeApi(APIView):
    permission_classes = [IsAuthenticated]
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'charge.html'

    def get(self, request):
        plans = get_list_or_404(BillingPlan)
        serializer = ListBillingPlanSerializer(plans, many=True)
        return Response({'plans': serializer.data, 'key': settings.STRIPE_PUBLISHABLE_KEY}, status=status.HTTP_200_OK)
