from django.db import connection
from rest_framework.exceptions import AuthenticationFailed

# from transport.serializers import CheckGetCitiesByCountrySerializer, CheckGetZipCodesByCitySerializer, CompanyListSerializer, ListCitiesSerializer, ListCompanyBlockSerializer, ListZipCodesSerializer

from .models import *
from .sql import *
from helpers.global_helper.object_generator import *
from .helpers import *
from .serializers import *


def get_prepare():
    query = sql_get_prepare()
    sql_data = execute_sql_query(query)
    return sql_data[0]


def get_cities_by_country(data):
    print(data)
    s = CheckGetCitiesByCountrySerializer(data=data)
    s.is_valid(raise_exception=True)
    objs = City.objects.filter(country_id=data['country'])
    res = ListCitiesSerializer(objs, many=True).data
    return res


def get_zip_codes_by_city(data):
    print(data)
    s = CheckGetZipCodesByCitySerializer(data=data)
    s.is_valid(raise_exception=True)
    objs = ZipCode.objects.filter(is_active=True, city_id=data['city'])
    res = ListZipCodesSerializer(objs, many=True).data
    return res


def get_cities_and_zip_codes_by_country(data):
    s = CheckGetCitiesByCountrySerializer(data=data)
    s.is_valid(raise_exception=True)
    query = sql_get_cities_and_zip_codes_by_country(data['country'])
    sql_data = execute_sql_query(query)
    res = sql_data[0]
    if not res['cities']:
        res['cities'] = []
        res['zip_codes'] = []
    return res


def get_cargo_details(cargo_id):
    query = sql_get_cargo_details(cargo_id)
    sql_data = execute_sql_query(query)
    with connection.cursor() as cursor:
        cursor.execute(query)
        sql_data = cursor.fetchone()
    print(sql_data)
    if not sql_data[0]:
        return {"message": "Ne postoji"}, 404
    res = sql_data[0][0]
    res = pretty_get_cargo_details(res)

    return res, 200


def get_cargo_list(*args, **kwargs):
    query = sql_get_cargo_list(*args, **kwargs)

    with connection.cursor() as cursor:
        cursor.execute(query)
        sql_data = cursor.fetchone()
    res = sql_data[0]
    if not res:
        return [], 200
    # res = pretty_get_cargo_list(res)
    print(len(res))

    # res = {
    #     "data": res,
    #     "cursor": get_preview_next_cursor(res, 'sort_by', *args, **kwargs)
    # }
    res = get_data_with_cursor_response(res, 'sort_by', *args, **kwargs)

    return res, 200


def get_my_cargo(token, *args, **kwargs):
    query = sql_get_my_cargo(token, *args, **kwargs)

    sql_data = execute_sql_query(query, many=True)

    if not sql_data:
        return []
    # sql_data = pretty_get_cargo_list(sql_data)

    return sql_data


def get_my_loading_spaces(token, *args, **kwargs):
    query = sql_get_my_loading_spaces(token, *args, **kwargs)

    sql_data = execute_sql_query(query, many=True)
    if not sql_data:
        return []
    # res = pretty_get_loading_space_list(sql_data)
    return sql_data


def get_my_stocks(token, *args, **kwargs):
    query = sql_get_my_stocks(token, *args, **kwargs)

    sql_data = execute_sql_query(query, many=True)
    if not sql_data:
        return []
    # res = pretty_get_stock_list(sql_data)
    return sql_data


def get_loading_spaces(pk, token, *args, **kwargs):
    print(kwargs)
    if pk:
        sql_data = call_sql_proc('get_loading_space', [pk])
        if not sql_data:
            return {}, 404
        # res = pretty_get_loading_space_details(sql_data[0])
        return sql_data, 200
    else:
        query = sql_get_loading_spaces_list(token, *args, **kwargs)
        sql_data = execute_sql_query(query, many=True)
        # sql_data = call_sql_proc('get_loading_space', [0])
        if not sql_data:
            return [], 200
        # res = pretty_get_loading_space_list(sql_data)
        # res = {
        #     "data": sql_data,
        #     "cursor": get_preview_next_cursor(sql_data, *args, **kwargs)
        # }
        res = get_data_with_cursor_response(sql_data, 'sort_by', *args, **kwargs)
        return res, 200


def get_stocks(pk, token, *args, **kwargs):
    if pk:
        sql_data = call_sql_proc('get_stock', [pk])
        if not sql_data:
            return {}, 404
        # res = pretty_get_stock_details(sql_data[0])
        return sql_data, 200
    else:
        query = sql_get_stocks_list(token, *args, **kwargs)
        sql_data = execute_sql_query(query, many=True)
        # sql_data = call_sql_proc('get_stock', [0])
        if not sql_data:
            return [], 200
        # res = pretty_get_stock_list(sql_data)
        # res = {
        #     "data": sql_data,
        #     "cursor": get_preview_next_cursor(sql_data, *args, **kwargs)
        # }
        res = get_data_with_cursor_response(sql_data, 'start_datetime', *args, **kwargs)
        return res, 200


def get_companies(token, *args, **kwargs):
    query = sql_get_company_list(token, *args, **kwargs)
    sql_data = execute_sql_query(query, many=True)
    if not sql_data:
        return []
    # res = sql_data
    # res = {
    #     "data": res,
    #     "cursor": get_preview_next_cursor(res, *args, **kwargs)
    # }
    res = get_data_with_cursor_response(sql_data, 'name', *args, **kwargs)
    return res

def get_companies_to_confirm(*args, **kwargs):
    query = sql_get_companies_to_confirm(*args, **kwargs)
    sql_data = execute_sql_query(query, many=True)
    if not sql_data:
        return []
    return sql_data

def get_company_details(pk):
    query = sql_get_company_details(pk)
    sql_data = execute_sql_query(query)
    if not sql_data:
        raise Http404()
    # res = pretty_get_company_details(sql_data)
    return sql_data


def get_blocked_companies(user):
    objs = CompanyBlockList.objects.filter(unblocked_at=None, my_company=user.company).select_related('blocked_company')
    ser = ListCompanyBlockSerializer(objs, many=True)
    return ser.data

def get_basic_backoffice_info(*args, **kwargs):
    query = sql_get_basic_backoffice_info(*args, **kwargs)
    sql_data = execute_sql_query(query)
    return sql_data

def get_fist_page_data(user, *args, **kwargs):
    query = sql_get_first_page_data(user.company_id, *args, **kwargs)
    sql_data = execute_sql_query(query, json_response=False)
    res = {
        "cargo": {
            "total_published_count": sql_data[0],
            "my_active_sum": sql_data[1]
        },
        "loading_space": {
            "total_published_count": sql_data[2],
            "my_active_sum": sql_data[3]
        },
        "stock": {
            "total_published_count": sql_data[4],
            "my_active_sum": sql_data[5]
        }
    }
    return res