
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from terraPorta.apps.accounts.models import Profile
from django.contrib.auth.models import User
from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.orgs.resources import OrganizationSerializer


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    is_active = serializers.BooleanField(default=False)
    org = OrganizationSerializer()

    def create(self, validated_data):
        org_data = validated_data.pop('org')
        user = User.objects.create(**validated_data)
        plain_password = validated_data['password']
        user.set_password(plain_password)
        user.save()
        Organization.objects.create(owner=user, **org_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_active', 'org')


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    is_active = serializers.BooleanField(default=False)

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        plain_password = validated_data['password']
        user.set_password(plain_password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_active')


class GetUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(read_only=True, required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    class Meta:
        model = Profile
        fields = ('id', 'user', 'location', 'state', 'birth_date')

class GetUserProfileSerializer(serializers.Serializer):
    profile = ProfileSerializer()
    user = GetUserSerializer()

    def to_representation(self, instance):
        instance = super(GetUserProfileSerializer, self).to_representation(instance)
        represent = {
            'username': instance['user']['username'],
            'email': instance['user']['email'],
            'first_name': instance['user']['first_name'],
            'last_name': instance['user']['last_name'],
            'location': instance['profile']['location'],
            'state': instance['profile']['state'],
            'birth_date': instance['profile']['birth_date']}
        return represent


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=8)
    repeated_password = serializers.CharField(required=True, min_length=8)


class UsernameResetSerializer(serializers.Serializer):
    new_username = serializers.CharField(required=True, min_length=4)


class PasswordSerializer(serializers.Serializer):
    """
    Serializes user passwords
    """
    current_password = serializers.CharField(required=True, min_length=8)
    new_password = serializers.CharField(required=True, min_length=8)
    repeated_password = serializers.CharField(required=True, min_length=8)

    def validate(self, data):
        """
        Validates new password
        """
        if data['new_password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords doesn't match!")

        return data
