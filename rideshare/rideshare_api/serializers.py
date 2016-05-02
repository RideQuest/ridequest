from django.contrib.auth.models import User
from rideshare_profile.models import Profile, Route
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serialize user."""

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize user profile."""

    class Meta:
        model = Profile
        fields = ('firstname', 'lastname', 'email', 'phonenumber',
                  'carbrand', 'carseat', 'petsallowed')
    class Meta:
        model = Route
        fields = ('in_profile', 'address_line1', 'address_line2',
                  'postal_code', 'city', 'state', 'destination_line1',
                  'destination_line2', 'destination_postal_code',
                  'destination_city', 'destination_state')
