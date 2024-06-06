import os
import random
import string

from django.http.response import Http404, HttpResponseNotFound
from rest_framework import exceptions
from helpers.global_helper.exceptions import api_exc
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.db import transaction, connection

from transport.constants import NEXT_CURSOR
from .constants import *


def get_token(headers):
    try:
        token = headers['Authorization'].split(' ')[1]
    except:
        raise AuthenticationFailed()
    else:
        return token

def get_token_or_empty(headers):
    try:
        token = headers['Authorization'].split(' ')[1]
    except:
        return ''
    else:
        return token


def call_sql_proc(proc_name, params=[]):
    with connection.cursor() as cursor:
        cursor.callproc(proc_name, params)
        sql_data = cursor.fetchall()
    print(sql_data)
    if sql_data[0][0] == 401:
        raise AuthenticationFailed()
    if sql_data[0][0] == 403:
        raise PermissionDenied()
    if sql_data[0][0] == 404:
        raise Http404()

    return sql_data[0][0]


def execute_sql_query(query, many=False, json_response=True):
    with connection.cursor() as cursor:
        cursor.execute(query)
        if many:
            sql_data = cursor.fetchall()
        else:
            sql_data = cursor.fetchone()

    if not json_response:
        return sql_data

    if many:
        check_data = sql_data[0][0]
    else:
        check_data = sql_data[0]
    if check_data == 401:
        raise AuthenticationFailed()

    return check_data


def format_ids(ids, delimeter='|'):
    ids = ids.replace(delimeter, ",")
    if ids[-1] == ',':
        ids = ids[:-1]
    ids = '(' + ids + ')'
    return ids


def get_parameters(data):
    res = {}
    print(data)
    passed = []
    for key, value in data.items():
        if value:
            res[key] = value
            passed.append(key)
    res['limit'] = 30 + 1
    return res


def get_ids_from_query_param(column, data):
    if not column: return ''
    query = column + ' in (' + ''
    res = data.split('|')
    for i in res:
        if i:
            query += i + ','
    query = query[:-1]
    query += ')'
    print(query)
    return query


def format_ids(ids, delimeter='|'):
    ids = ids.replace(delimeter, ",")
    if ids[-1] == ',':
        ids = ids[:-1]
    ids = '(' + ids + ')'
    return ids

def format_string(arr, delimeter='|'):
    arr = arr.replace(delimeter, "','")
    if arr[-3:] == "','":
        arr = arr[:-3]
    arr = "('" + arr + "')"
    print(arr)
    return arr


def get_join_string(JOIN_ARR):
    JOIN_STRING = ''
    if not JOIN_ARR: return ''
    for i in JOIN_ARR:
        JOIN_STRING += i + ' '

    return JOIN_STRING


def get_where_string(WHERE_ARR):
    WHERE_STRING = ''
    if not WHERE_ARR: return ''
    for count, i in enumerate(WHERE_ARR):
        if count < len(WHERE_ARR) - 1:
            WHERE_STRING += i + ' and '
        else:
            WHERE_STRING += i

    if WHERE_STRING:
        WHERE_STRING = 'WHERE ' + WHERE_STRING

    return WHERE_STRING


def get_where_string_or(WHERE_ARR):
    WHERE_STRING = ''
    if not WHERE_ARR: return ''
    for count, i in enumerate(WHERE_ARR):
        if count < len(WHERE_ARR) - 1:
            WHERE_STRING += i + ' or '
        else:
            WHERE_STRING += i

    WHERE_STRING = f'({WHERE_STRING})'

    return WHERE_STRING


def get_bool_from_string(a):
    if a == '0': return False
    return True

def check_next_cursor(data, *args, **kwargs):
    if int(kwargs.get(LIMIT)) == len(data):
        data = data[:-1]



def get_preview_next_cursor(data, cursor='id', *args, **kwargs):
    previus_cursor = None
    next_cursor = None
    # if NEXT_CURSOR in kwargs:
    #     previus_cursor = kwargs.get(NEXT_CURSOR)
    if int(kwargs.get(LIMIT)) == len(data):
        next_cursor = data[-2][cursor]
    print(kwargs.get(LIMIT))
    print(len(data))
    obj = {
        'previus_cursor': previus_cursor,
        'next_cursor': next_cursor
    }
    return obj

def get_data_with_cursor_response(data, cursor='id', *args, **kwargs):
    cur_data = get_preview_next_cursor(data, cursor, *args, **kwargs)
    if cur_data['next_cursor']:
        data = data[:-1]
    res = {
        "data": data,
        "cursor": cur_data
    }
    return res


def generate_cargo_load_unload_sql_filter(*args, **kwargs):
    """
    Funkcija generira query za filtriranje polazista i odredista
    za teret.
    Vraca tuple (join, where dio, having)
    """
    need_join = False
    join_query = ''
    load_query = ''
    load_where_arr = []
    load_where_string = ''
    load_where_or_arr = []
    load_where_or_string = ''
    unload_where_arr = []
    unload_where_string = ''
    unload_where_or_arr = []
    unload_where_or_string = ''
    from_exists = (COUNTRIES_FROM in kwargs or CITIES_FROM in kwargs or ZIP_CODES_FROM in kwargs)
    to_exists = (COUNTRIES_TO in kwargs or CITIES_TO in kwargs or ZIP_CODES_TO in kwargs)
    need_having = (from_exists and to_exists)
    having_query = ''

    if from_exists:
        need_join = True
        load_where_arr.append("tc2.type = 'load'")
    if to_exists:
        need_join = True
        unload_where_arr.append("tc2.type = 'unload'")

    if COUNTRIES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.country_id in {format_ids(kwargs.get(COUNTRIES_FROM))}")
    if COUNTRIES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.country_id in {format_ids(kwargs.get(COUNTRIES_TO))}")
    if CITIES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.city_id in {format_ids(kwargs.get(CITIES_FROM))}")
    if CITIES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.city_id in {format_ids(kwargs.get(CITIES_TO))}")
    if ZIP_CODES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.zip_code_id in {format_ids(kwargs.get(ZIP_CODES_FROM))}")
    if ZIP_CODES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.zip_code_id in {format_ids(kwargs.get(ZIP_CODES_TO))}")

    load_where_or_string = get_where_string_or(load_where_or_arr)
    unload_where_or_string = get_where_string_or(unload_where_or_arr)

    if load_where_or_string:
        load_where_arr.append(load_where_or_string)
    if unload_where_or_string:
        unload_where_arr.append(unload_where_or_string)

    load_where_string = get_where_string(load_where_arr)
    unload_where_string = get_where_string(unload_where_arr)
    if load_where_string: load_where_string = f"({load_where_string.split(' ', 1)[1]})"
    if unload_where_string: unload_where_string = f"({unload_where_string.split(' ', 1)[1]})"
    if load_where_string and unload_where_string:
        query = f'''
            ({load_where_string} or {unload_where_string})
        '''
    elif load_where_string:
        query = f'''
            ({load_where_string})
        '''
    elif unload_where_string:
        query = f'''
            ({unload_where_string})
        '''
    else:
        query = ''
    if need_join:
        join_query = 'inner join transport_cargoloadunload tc2 on tc2.cargo_id = tc.id'
    if need_having:
        having_query = 'having count(distinct(tc2.type)) > 1'
    return join_query, query, having_query


def generate_loading_space_starting_point_destination_sql_filter(*args, **kwargs):
    """
    Funkcija generira query za filtriranje polazista i odredista
    za teret.
    Vraca tuple (join, where dio, having)
    """
    need_join = False
    join_query = ''
    load_query = ''
    load_where_arr = []
    load_where_string = ''
    load_where_or_arr = []
    load_where_or_string = ''
    unload_where_arr = []
    unload_where_string = ''
    unload_where_or_arr = []
    unload_where_or_string = ''
    from_exists = (COUNTRIES_FROM in kwargs or CITIES_FROM in kwargs or ZIP_CODES_FROM in kwargs)
    to_exists = (COUNTRIES_TO in kwargs or CITIES_TO in kwargs or ZIP_CODES_TO in kwargs)
    need_having = (from_exists and to_exists)
    having_query = ''

    if from_exists:
        need_join = True
        load_where_arr.append("tc2.type = 'starting'")
    if to_exists:
        need_join = True
        unload_where_arr.append("tc2.type = 'destination'")

    if COUNTRIES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.country_id in {format_ids(kwargs.get(COUNTRIES_FROM))}")
    if COUNTRIES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.country_id in {format_ids(kwargs.get(COUNTRIES_TO))}")
    if CITIES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.city_id in {format_ids(kwargs.get(CITIES_FROM))}")
    if CITIES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.city_id in {format_ids(kwargs.get(CITIES_TO))}")
    if ZIP_CODES_FROM in kwargs:
        load_where_or_arr.append(f"tc2.zip_code_id in {format_ids(kwargs.get(ZIP_CODES_FROM))}")
    if ZIP_CODES_TO in kwargs:
        unload_where_or_arr.append(f"tc2.zip_code_id in {format_ids(kwargs.get(ZIP_CODES_TO))}")

    load_where_or_string = get_where_string_or(load_where_or_arr)
    unload_where_or_string = get_where_string_or(unload_where_or_arr)

    if load_where_or_string:
        load_where_arr.append(load_where_or_string)
    if unload_where_or_string:
        unload_where_arr.append(unload_where_or_string)

    load_where_string = get_where_string(load_where_arr)
    unload_where_string = get_where_string(unload_where_arr)
    if load_where_string: load_where_string = f"({load_where_string.split(' ', 1)[1]})"
    if unload_where_string: unload_where_string = f"({unload_where_string.split(' ', 1)[1]})"
    if load_where_string and unload_where_string:
        query = f'''
            ({load_where_string} or {unload_where_string})
        '''
    elif load_where_string:
        query = f'''
            ({load_where_string})
        '''
    elif unload_where_string:
        query = f'''
            ({unload_where_string})
        '''
    else:
        query = ''
    if need_join:
        join_query = 'inner join transport_startingpointdestination tc2 on tc2.loading_space_id = tc.id'
    if need_having:
        having_query = 'having count(distinct(tc2.type)) > 1'
    return join_query, query, having_query


def update_company_format_data(data):
    res = {}
    for key, value in data.items():
        res[key.split('_', 1)[1]] = value
    print(res)
    return res


def generate_random_file_name(name, str_size=7):
    """
    Generiranje random name za dokument
    """
    allowed_chars = string.ascii_letters + string.digits
    ext = os.path.splitext(name)[-1].lower()
    print(ext)
    root_name = os.path.splitext(name)[0]
    return root_name + '_' + ''.join(random.choice(allowed_chars) for x in range(str_size)) + ext