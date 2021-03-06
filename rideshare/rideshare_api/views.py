# from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ProfileSerializer, RouteSerializer, AvatarSerializer
from django.contrib.auth.models import User
from rideshare_profile.models import Profile, Route, Avatar
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.gis.measure import D
from django.contrib.gis import geos
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import parsers, renderers
from django.utils.six import text_type
import base64
import binascii
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework import status
from django.contrib.gis.db.models.functions import AsGeoJSON
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,
                      parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)

        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')

        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]

        credentials = {
            'username': userid,
            'password': password
        }
        user = authenticate(**credentials)
        if user is None:
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        token, created = Token.objects.get_or_create(user=user)
        try:
            profile = Profile.objects.get(user=user)
            return Response({'token': token.key,
                             'user_id': user.id,
                             'profile_id': profile.id})
        except ObjectDoesNotExist:
            return Response({'token': token.key,
                             'user_id': user.id,
                             'profile_id': None})


def get_authorization_header(request):
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class ModifyUserEndpoint(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for modifying a user."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)


class CreateUserEndpoint(generics.CreateAPIView):
    """Endpoint for creating a user."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = UserSerializer(data={
            'username': request.data['username'],
            'email': request.data['email'],
            'password': request.data['password']
            })
        validation = serializer.is_valid()
        if validation:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileCreateEndpoint(generics.CreateAPIView):
    """Endpoint for creating a profile."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)

    def create(self, request):
        serializer = ProfileSerializer(data={
            'user': request.user.id,
            'firstname': request.data['firstname'],
            'lastname': request.data['lastname'],
            'email': request.data['email'],
            'phonenumber': request.data['phonenumber'],
            'carbrand': request.data['carbrand'],
            'carseat': request.data['carseat'],
            'petsallowed': request.data['petsallowed']
            })
        validation = serializer.is_valid()
        if validation:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileEndpoint(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for profile model."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)


class AddAvatarEndpoint(generics.CreateAPIView):
    """Add an profile pic to a profile."""

    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (BasicAuthentication, TokenAuthentication)

    def create(self, request):
        serializer = AvatarSerializer(data={
            'profile': request.user.profile.id,
            'image_url': request.data,
            })

        validation = serializer.is_valid()
        if validation:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateAvatarEndpoint(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for updating profile pic."""

    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (BasicAuthentication, TokenAuthentication)

    def update(self, request, *args, **kwargs):
        """Check if avatar is in request and updates it if it is."""
        serializer = AvatarSerializer(data={
            'profile': request.user.profile.id,
            'image_url': request.data,
            })

        if 'image_url' in request.data:
            image = self.get_object()
            image.cleanup_pre_delete()
            image.delete()
            image.cleanup_post_delete()

            image_url = request.data['image_url']
            profile = request.user.profile.id
            profile.image_url.save(image_url.name, image_url)

        validation = serializer.is_valid()
        if validation:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteEndpoint(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for profile model."""

    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)


class RouteCreateEndpoint(generics.CreateAPIView):
    """Endpoint for profile model."""

    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)

    def create(self, request):
        lat = request.data['lat']
        lng = request.data['lng']
        point = geos.Point(float(lng), float(lat))
        token_profile = Profile.objects.filter(user=request.user)[0]
        serializer = RouteSerializer(data={
            'user': int(token_profile.id),
            'start_point': point
            })
        validation = serializer.is_valid()
        if validation:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteQueryEndpoint(generics.ListAPIView):
    """Endpoint for query."""
    serializer_class = RouteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)

    def get_queryset(self):
        request = self.request
        lat = request.GET['lat']
        lng = request.GET['lng']
        point = geos.Point(float(lng), float(lat))
        result = Route.objects.filter(
            start_point__distance_lt=(point, D(km=1))
        )
        return result
