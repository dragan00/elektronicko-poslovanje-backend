from helpers.global_helper.exceptions import *
from helpers.global_helper.object_generator import *
from .models import *
from transport.models import *
import json
from django.db import transaction
from .serializers import *
from rest_framework.authtoken.models import Token
from .selector import *
from .helpers import *
from transport.services import upload_company_documents
from transport.helpers import *
from transport.validators import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from mailer.password_mailer import send_account_password_email
from helpers.global_helper.exceptions import api_exc

def test_insert_multiple_accounts():
    arr = []
    for i in range(100):
        arr.append({
            "account_full_name": f"Puno ime i prezime {i+1}",
            "account_password": "pass",
            "account_email": f"{i+1}@test.com",
            "account_phone_number": f"063{str(i+1) * 6}",
            "company": None,
            "company_name": f"Company {i+1}",
            "accout_languages":[1,2],
            "company_address": f"Adresa {i+1}",
            "company_emails": [f"{i+1}mail@neuros-team.hr"],
            "company_OIB": f"{str(i+1)*10}",
            "company_year": 2015,
            "company_web": f"https://neuros-{i+1}.hr",
            "company_numbers": [
                {
                    "number": f"063{str(i+1) * 7 + str(i+1) * 1}",
                    "type": "fax"
                },
                {
                    "number": f"063{str(i+1) * 7 + str(i+1) * 2}",
                    "type": "tel"
                }
            ]
        })
    for data in arr:
        print(data)
        #Registracija Korisnika
        acc = Account(
            name = data['account_full_name'],
            email = data['account_email'],
            phone_number = data['account_phone_number']
        )
        print("Dodan account, ide sifra")
        acc.set_password(data['account_password'])

        if data['company']:
            acc.company_id = data['company']
            acc.save()
        else:
            # acc.languages.add(data['languages'])
            #Registracija poduzeca
            acc.save()
            company = Company.objects.create(
                name=data['company_name'],
                address=data['company_address'],
                OIB=data['company_OIB'],
                year=data['company_year'],
                web=data['company_web'],
                creator=acc
            )
            acc.company = company
            acc.save()
            for i in data['accout_languages']:
                print(i)
                acc.languages.add(Language.objects.get(id=i))
            company_nums = []
            for i in data['company_numbers']:
                company_nums.append(CompanyNumber(number=i['number'], type=i['type'], company=company))
            CompanyNumber.objects.bulk_create(company_nums)
            emails = []
            for i in data['company_emails']:
                emails.append(CompanyMail(email=i, company=company))
            CompanyMail.objects.bulk_create(emails)

    #     token, created = Token.objects.get_or_create(user=acc)

    # data = get_user(token)

    return arr

@transaction.atomic
def register_account(formdata, files, token):
    res = {
        "data": [],
        "message": ''
    }
    just_account = False
    try:
        data = json.loads(formdata['data'])
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))
    if 'company' in data and data['company']:
        just_account = True
        pswrd = generate_random_account_password()
        s = CheckRegisterAccountSerializer(data=data)
    else:
        pswrd = data['account_password']
        s = CheckRegisterCompanySerializer(data=data)
    s.is_valid(raise_exception=True)
    data['account_password'] = make_password(pswrd)
    email = data['account_email']
    print(data['account_password'])
    data['files'] = []

    if Account.objects.filter(email=email).exists():
        res['message'] = f'Korisnik s e-mailom "{email}" već postoji'
        return res

    if files:
        if not validate_company_documents(files):
            print("Nedozvoljene ekstenzije, vrati error.")
        for file in files:
            title = file.name
            file.name = generate_random_file_name(file.name)
            data['files'].append({
                'path': f'files/{file.name}',
                'title': title
            })

    _data = json.dumps(data)
    sql_data = call_sql_proc('insert_update_account_and_company', [False, _data, token])
    print(sql_data)

    if files:
        for file in files:
            with open(f'mediafiles/files/{file.name}', 'wb') as fp:
                fp.write(file.read())
    print("==")

    if not just_account:
        token = Token.objects.create(user_id=sql_data)
        res_data = get_user(token)
    else:
        res_data = get_company_contact_accounts(data['company'])
        send_account_password_email.after_response(email, pswrd, data['company'])
    res['data'] = res_data
    return res

@transaction.atomic
def _register_account(formdata, files):
    try:
        data = json.loads(formdata['data'])
        print(data)
        #Registracija Korisnika
        acc = Account(
            name = data['account_full_name'],
            email = data['account_email'],
            phone_number = data['account_phone_number']
        )
        print("Dodan account, ide sifra")
        acc.set_password(data['account_password'])


        if data['company']:
            acc.company_id = data['company']
            acc.save()
        else:
            # acc.languages.add(data['languages'])
            #Registracija poduzeca
            acc.save()
            company = Company.objects.create(
                name=data['company_name'],
                # address=data['company_address'],
                OIB=data['company_OIB'],
                year=data['company_year'],
                web=data['company_web'],
                country_id=data['company_country'],
                city_id=data['company_city'],
                zip_code_id=data['company_zip_code'],
                creator=acc
                # country_id=data['company_country'],
                # city_id=data['company_city'],
                # zip_code_id=data['company_zip_code']
            )
            acc.company = company
            acc.save()
            for i in data['account_languages']:
                print(i)
                acc.languages.add(Language.objects.get(id=i))
            company_nums = []
            for i in data['company_numbers']:
                company_nums.append(CompanyNumber(number=i['number'], type=i['type'], company=company))
            CompanyNumber.objects.bulk_create(company_nums)
            emails = []
            for i in data['company_emails']:
                emails.append(CompanyMail(email=i, company=company))
            CompanyMail.objects.bulk_create(emails)

            if files:
                upload_company_documents(company.id, files)

        token, created = Token.objects.get_or_create(user=acc)

        data = get_user(token)

        return data
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))

def update_account(pk, data):
    obj = Account.objects.get(id=pk)
    data = pretty_update_account_request_data(data)
    ser = UpdateAccountSerializer(instance=obj, data=data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()

    res = get_user_by_id(pk)
    return res

def update_panes(data, account):
    s = CheckUpdatePanesSerializer(data=data)
    s.is_valid(raise_exception=True)
    account.panes = data['panes']
    account.save()
    return True

def change_avatar(files, user):
    img = None
    if not files:
        print("Nema fotografije")
    else:
        img = files[0]
    user.avatar = img
    user.save()
    res = {
        'avatar': user.avatar.name
    }
    return res



def remove_account(data, user):
    s = CheckRemoveAccountSerializer(data=data)
    s.is_valid(raise_exception=True)
    print(s.data)
    obj = get_object_or_404(Account, id=s.data['account_id'])
    print(obj)
    if obj.company_id != user.company_id:
        raise PermissionDenied()
    if Account.objects.filter(is_active=True, company_id=obj.company_id).count() <= 1:
        raise PermissionDenied()
    obj.is_active = False
    obj.save()
    Token.objects.filter(user=obj).delete()
    return True