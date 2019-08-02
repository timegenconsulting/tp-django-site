
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from terraPorta.apps.billing.models import Payment, BillingPlan, Provider


class CreatePaymentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%m/%d/%Y %H:%M:%S", input_formats=["%m/%d/%Y %H:%M:%S"])

    def create(self, validated_data):
        record_payment = Payment.objects.create(**validated_data)
        return record_payment

    class Meta:
        model = Payment
        fields = ('id', 'user', 'org', 'amount',
                  'order_id', 'created', 'transaction_id',
                  'balance_transaction', 'status', 'full_response',
                  'failure_code', 'failure_message', 'provider')


class RequestPaymentSerializer(serializers.Serializer):
    user = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    order_id = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Payment.objects.all())]
    )

class ListBillingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPlan
        fields = ('id', 'provider', 'provider_id', 'days', 'price', 'description')

    def to_representation(self, instance):
        instance = super(ListBillingPlanSerializer, self).to_representation(instance)
        represent = {
            'id': instance['id'],
            'days': instance['days'],
            'price': instance['price'] / 100,
            'description': instance['description'],
            'provider_id': instance['provider_id']
        }
        return represent


class BillingPlanSerializer(serializers.ModelSerializer):
    days = serializers.IntegerField(required=True)
    price = serializers.FloatField(required=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        source='provider',
        queryset=Provider.objects.all()
    )

    def create(self, validated_data):
        validated_data['price'] = validated_data['price'] * 100
        plan = BillingPlan.objects.create(**validated_data)
        return plan

    class Meta:
        model = BillingPlan
        fields = ('id', 'days', 'provider_id', 'provider', 'price', 'description')

    def to_representation(self, instance):
        instance = super(BillingPlanSerializer, self).to_representation(instance)
        represent = {
            'id': instance['id'],
            'days': instance['days'],
            'price': instance['price'] / 100,
            'description': instance['description'],
            'provider_id': instance['provider_id']
        }
        return represent


class GetBillingPlanSerializer(serializers.ModelSerializer):
    provider_id = serializers.PrimaryKeyRelatedField(
        source='provider',
        queryset=Provider.objects.all()
    )
    class Meta:
        model = BillingPlan
        fields = ('id', 'days', 'price', 'provider', 'provider_id', 'description')

    def to_representation(self, instance):
        instance = super(GetBillingPlanSerializer, self).to_representation(instance)
        represent = {
            'id': instance['id'],
            'days': instance['days'],
            'price': instance['price'] / 100,
            'description': instance['description'],
            'provider_id': instance['provider_id']
        }
        return represent


class BillingHistorySerializer(serializers.ModelSerializer):
    org = serializers.ReadOnlyField(source='org.name')
    created = serializers.DateTimeField(format="%m-%d-%Y %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'user', 'org', 'amount',
                  'order_id', 'created', 'transaction_id',
                  'balance_transaction', 'status', 'full_response',
                  'failure_code', 'failure_message', 'provider')

    def to_representation(self, instance):
        instance = super(BillingHistorySerializer, self).to_representation(instance)
        represent = {
            'id': instance['id'],
            'user': instance['user'],
            'org': instance['org'],
            'amount': instance['amount'] / 100,
            'order_id': instance['order_id'],
            'created': instance['created'],
            'status': instance['status'],
            'provider': instance['provider']

        }
        return represent
