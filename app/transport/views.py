from django.shortcuts import render
from rest_framework import views, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from accounts.services import update_panes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied

from django.db import connection, transaction
from .helpers import *

from .services import *
from .selectors import *
from .permissions import *

class TestApiView(APIView):
    def get(self, request):
        # from firebase_admin.messaging import Message
        # from push_notifications import push_transport
        # from push_notifications import push_transport
        # data = {"load_unload":[{"country":7,"city":None,"zip_code":None,"from_date":"","to_date":"","from_time":"","to_time":"","type":"unload","start_datetime":None,"end_datetime":None},{"country":4,"city":2758,"zip_code":51914,"place":None,"from_date":"2021-09-20T12:50:44.860Z","to_date":"","from_time":"","to_time":"","type":"load","start_datetime":"2021-09-20 02:50","end_datetime":None}],"cargo":{"goods_types":[],"cargo_note":[{"lang":"hr","cargo_note":""},{"lang":"en","cargo_note":""},{"lang":"de","cargo_note":""}],"length":13.6,"width":2.4,"weight":24,"price":None,"exchange":False},"vehicle":{"vehicle_types":[],"vehicle_upgrades":[],"vehicle_equipment":[],"contact_accounts":[1],"vehicle_note":[{"lang":"hr","vehicle_note":""},{"lang":"en","vehicle_note":""},{"lang":"de","vehicle_note":""}]},"auction":{"auction":False,"start_price":None,"min_down_bind_percentage":None,"auction_end_datetime":None}}
        # # # res = push_transport.send_push_notification_by_user_filter({"load_unload":[{"country":9,"city":239,"zip_code":4122,"from_date":"","to_date":"","from_time":"","to_time":"","type":"unload","start_datetime":None,"end_datetime":None},{"country":4,"city":2758,"zip_code":51915,"place":None,"from_date":"","to_date":"","from_time":"","to_time":"","type":"unload","start_datetime":None,"end_datetime":None},{"country":7,"city":5379,"zip_code":58938,"place":None,"from_date":"2021-09-17T16:07:34.539Z","to_date":"","from_time":"","to_time":"","type":"load","start_datetime":"2021-09-17 06:07","end_datetime":None}],"cargo":{"goods_types":[8],"cargo_note":[{"lang":"hr","cargo_note":""},{"lang":"en","cargo_note":""},{"lang":"de","cargo_note":""}],"length":13.6,"width":2.4,"weight":24,"price":560,"exchange":False},"vehicle":{"vehicle_types":[5],"vehicle_upgrades":[],"vehicle_equipment":[],"contact_accounts":[1],"vehicle_note":[{"lang":"hr","vehicle_note":""},{"lang":"en","vehicle_note":""},{"lang":"de","vehicle_note":""}]},"auction":{"auction":False,"start_price":None,"min_down_bind_percentage":None,"auction_end_datetime":None}}, 26)
        # res = push_transport.send_push_notification_by_user_filter(data, 14, type='c', exclude_ids=[])
        # # push_transport.send_push_insert_auction.after_response(22, "78d3a9c0d423c4d22b74c2b8de88fb857b0eb2ce")
        # return Response(res, 200)
        # insert_vehicle_equipment()
        # insert_bih_cities_and_zip_codes()
        # fill_basic_data_in_db()
        # from accounts.services import test_insert_multiple_accounts
        # res = test_insert_multiple_accounts()
        send_push_notification([2], 'test', 'test')
        return Response('res', 200)

    # def dispatch(self, *args, **kwargs):
    #     response = super().dispatch(*args, **kwargs)
    #     print("Queries Counted: {}".format(len(connection.queries)))
    #     return response

class CountryViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer

class CityViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    queryset = City.objects.all()
    serializer_class = InsertCitiesSerializer

    def list(self, request, *args, **kwargs):
        res = get_cities_and_zip_codes_by_country(request.GET)
        return Response(res)

class CityApiView(APIView):
    """
    Mislim da se ne koristi zbog viewseta
    """
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        res = get_cities_and_zip_codes_by_country(request.GET)
        return Response(res)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response

class ZipCodeViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    queryset = ZipCode.objects.all()
    serializer_class = InsertZipCodeSerializer

    def list(self, request, *args, **kwargs):
        res = get_zip_codes_by_city(request.GET)
        return Response(res)

class ZipCodeApiView(APIView):
    """
    Mislim da vise ne koristi
    """
    def get(self, request, *args, **kwargs):
        res = get_zip_codes_by_city(request.GET)
        return Response(res)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response


class PrepareApiView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        res = get_prepare()
        return Response(res, 200)


class CargoApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    class InputSerializer(serializers.Serializer):
        cargo_id = serializers.IntegerField(required=True)

    def get(self, request, *args, **kwargs):
        cargo_id = kwargs.get('cargo_id')
        if cargo_id:
            can_view_cargo_details(cargo_id, request.user)
            res, code = get_cargo_details(int(cargo_id))
        else:
            res, code = get_cargo_list(get_token(request.headers), **get_parameters(request.GET))
        return Response(res, code)

    def post(self, request, *args, **kwargs):
        res = insert_cargo(request.data, get_token(request.headers))
        return Response(res, 200)

    def put(self, request, cargo_id=None, *args, **kwargs):
        res = update_cargo(request.data, get_token(request.headers), cargo_id)
        return Response(res, 200)



class CloseCargoApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    def post(self, request, pk=None, *args, **kwargs):
        res, code = close_cargo(pk, request.user)
        res, code = get_cargo_details(int(pk))
        return Response(res, code)

class AuctionApiView(APIView):
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        res = insert_auction(request.data, get_token(request.headers))
        return Response(res, 200)


class GetMyCargoApiView(APIView):
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        res = get_my_cargo(get_token(request.headers), **get_parameters(request.GET))
        return Response(res, 200)


class GetMyLoadingSpacesApiView(APIView):
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        res = get_my_loading_spaces(get_token(request.headers), **get_parameters(request.GET))
        return Response(res, 200)


class GetMyStocksApiView(APIView):
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        res = get_my_stocks(get_token(request.headers), **get_parameters(request.GET))
        return Response(res, 200)


class LoadingSpaceApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            can_view_loading_space_details(pk, request.user)
        res, code = get_loading_spaces(pk, get_token(request.headers), **get_parameters(request.GET))
        return Response(res, code)

    def post(self, request, *args, **kwargs):
        res = insert_loading_space(request.data, get_token(request.headers))
        return Response(res, 200)

    def put(self, request, pk=None, *args, **kwargs):
        res = update_loading_space(request.data, get_token(request.headers), pk)
        return Response(res, 200)

class CloseLoadingSpaceApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    def post(self, request, pk=None, *args, **kwargs):
        res, code = close_loading_space(pk, request.user)
        res, code = get_loading_spaces(pk, '')
        return Response(res, code)


class StockApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            can_view_stock_details(pk, request.user)
        res, code = get_stocks(pk, get_token(request.headers), **get_parameters(request.GET))
        return Response(res, code)

    def post(self, request, *args, **kwargs):
        res = insert_stock(request.data, get_token(request.headers), request.FILES.getlist('files'))
        return Response(res, 201)

    def put(self, request, pk=None, *args, **kwargs):
        print(pk)
        res = update_stock(request.data, get_token(request.headers), pk)
        return Response(res, 200)

class StockImageApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk=None, *args, **kwargs):
        can_upload_stock_images(pk, request.user)
        res = upload_stock_images(pk, request.FILES.getlist('files'), request.user)
        return Response(res)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response

class RemoveStockImageApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk=None, image_id=None, *args, **kwargs):
        can_remove_stock_image(image_id, pk, request.user)
        res = remove_stock_image(image_id, pk)
        return Response(res, 200)

class CloseStockApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    def post(self, request, pk=None, *args, **kwargs):
        res, code = close_stock(pk, request.user)
        res, code = get_stocks(pk, '')
        return Response(res, code)

class CompanyApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            can_view_company_details(pk, request.user)
            res = get_company_details(pk)
        else:
            res = get_companies(get_token(request.headers), **get_parameters(request.GET))
        return Response(res, 200)

    def put(self, request, pk=None, *args, **kwargs):
        res = update_company(pk, request.data, request.FILES.getlist('files'), get_token_or_empty(request.headers))
        return Response(res)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response

class CompanyDocumentApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None, *args, **kwargs):
        res = upload_company_documents(pk, request.FILES.getlist('files'), request.user, is_update=False)
        return Response(res, 200)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        print("Queries Counted: {}".format(len(connection.queries)))
        return response

class RemoveCompanyDocumentApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk=None, document_id=None, *args, **kwargs):
        res = remove_company_document(document_id, request.user)
        return Response(res, 200)

class BlockCompanyApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        res = get_blocked_companies(request.user)
        return Response(res, 200)

    def post(self, request, *args, **kwargs):
        res = block_company(request.data, request.user)
        return Response("POST", 200)


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

class CompanyAvatarApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        res = change_company_avatar(request.FILES.getlist('files'), request.user)
        return Response(res)

class ConfirmCompanyApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAdminUser, )

    def post(self, request, *args, **kwargs):
        res = confirm_company(request.data, request.user)
        return Response(200)

class CompaniesToConfirmApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAdminUser, )

    def get(self, request, *args, **kwargs):
        if STATUS in request.GET:
            status = format_string(request.GET[STATUS])
        else:
            status = [NEED_CONFIRM]
        print(status)
        res = get_companies_to_confirm(**get_parameters(request.GET))
        return Response(res, 200)


class BasicBackofficeInfoApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAdminUser, )

    def get(self, request, *args, **kwargs):
        res = get_basic_backoffice_info(*args, **kwargs)
        return Response(res, 200)

class FirstPageApiView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        res = get_fist_page_data(request.user, *args, **kwargs)
        return Response(res, 200)