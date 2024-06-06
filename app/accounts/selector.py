from rest_framework.exceptions import AuthenticationFailed
from .sql import *
from django.db import transaction
from django.db import connection
from helpers.global_helper.object_generator import *


def get_user(token):
    query = sql_get_user(token)

    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchone()
    res = data[0][0]
    if not data[0][0]['account']:
        raise AuthenticationFailed()
    res = pretty_get_user(res)
    # print(res)

    return res


def get_user_by_id(id):
    query = sql_get_user_by_id(id)

    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchone()
    res = data[0][0]
    # if not data[0][0]['account']:
    #     raise AuthenticationFailed()
    # res = pretty_get_user(res)
    print(res)

    return res


def get_company_contact_accounts(company_id):
    query = sql_get_company_contact_accounts(company_id)
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchone()
    res = data[0]
    return res
