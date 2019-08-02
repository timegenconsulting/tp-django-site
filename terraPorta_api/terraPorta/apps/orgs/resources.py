from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from terraPorta.apps.orgs.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=Organization.objects.all())]
            )

    # def create(self, validated_data):
    #     org = Organization.objects.create(**validated_data)
    #     return org

    class Meta:
        model = Organization
        fields = ('id', 'name', 'location', 'state', 'active')


class ListOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'owner', 'location', 'state', 'active', 'billing_date')


class OrgSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True, required=False)
    class Meta:
        model = Organization
        fields = ('id', 'name', 'owner', 'members', 'location', 'state', 'active', 'requests_no', 'billing_date')
