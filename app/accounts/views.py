from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import connection
from rest_framework import viewsets, mixins, generics
from fcm_django.models import FCMDevice

from .models import Account
from .services import *
from .serializers import *
from .selector import *


# class BasicUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         fields = (
#             'id', 'name', 'email', 'is_admin', 'phone_number', 'address')
from transport.helpers import get_token_or_empty
from transport.constants import ACTIVE, NEED_CONFIRM

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        res = {
            "message": '',
            "data": []
        }
        request.data['username'] = request.data['email']
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = serializer.validated_data['user']
        else:
            res['message'] = 'Neispravan email ili lozinka'
            return Response(res, 200)

        if user.id == 1:
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            print(user)
            data = get_user(token)

            res = {
                "message": '',
                "data": data
            }

            return Response(res, 200)

        if not user.company.status in [ACTIVE, NEED_CONFIRM]:
            print(user.company.status)
            print('Nije aktivan')
            res['message'] = 'Neispravan email ili lozinka'
            return Response(res, 200)
            return Response({'message': 'Rejected!'}, 403)

        token, created = Token.objects.get_or_create(user=user)

        if 'fcm_token' in request.data:
            fcm, created = FCMDevice.objects.get_or_create(
                user=user, registration_id=request.data['fcm_token'], type='web')
            if not created and not fcm.active:
                fcm.active = True
                fcm.save()

        data = get_user(token)

        res = {
            "message": '',
            "data": data
        }

        return Response(res, 200)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response

class Logout(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            print(token)
            tok = Token.objects.get(key=token)
            tok.delete()
            try:
                FCMDevice.objects.filter(user=request.user).delete()
            except:
                pass
            return Response(status=200)
        except Exception as e:
            print(str(e))
            return Response({'message': str(e)}, status.HTTP_400_BAD_REQUEST)


class GetUserApiView(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ('id', 'full_name')

    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        if 'token' in request.GET:
            token = request.GET['token']
            res = get_user(token)
            return Response(res, 200)
        else:
            return Response({"message": "Token"}, status.HTTP_401_UNAUTHORIZED)


class RegisterApiView(APIView):
    def post(self, request, *args, **kwargs):
        res = register_account(request.data, request.FILES.getlist('files'), get_token_or_empty(request.headers))
        return Response(res, 200)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response


class UpdateAccountApiView(APIView):
    def put(self, request, pk=None, *args, **kwargs):
        res = update_account(pk, request.data)
        return Response(res, 200)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response


class PanesApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        update_panes(request.data, request.user)
        return Response(200)


class AvatarApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        res = change_avatar(request.FILES.getlist('files'), request.user)
        return Response(res)

class ChangePasswordView(generics.UpdateAPIView):

    queryset = Account.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response


class RemoveAccountApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        res = remove_account(request.data, request.user)
        return Response(200)

class AccountViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Account.objects.filter(is_active=True).select_related('company')
    serializer_class = BackofficeAccountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAdminUser, )

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response