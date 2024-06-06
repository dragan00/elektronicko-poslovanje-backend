from .exceptions import *

def prepare_data_for_register_account(data):
    try:
        obj = {
            "name": data['account_full_name'],
            "email": data['account_email'],
            "phone_number": data['account_phone_number']
        }
        return obj
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))

def pretty_get_user(data):
    if data['account']:
        data['account'] = data['account'][0]
    if data['prepare']:
        data['prepare'] = data['prepare'][0]
    if not data['prepare']['stock_types']:
        data['prepare']['stock_types'] = []
    if not data['prepare']['stock_equipment']:
        data['prepare']['stock_equipment'] = []
    if not data['prepare']['goods_types']:
        data['prepare']['goods_types'] = []
    if not data['prepare']['vehicle_types']:
        data['prepare']['vehicle_types'] = []
    if not data['prepare']['vehicle_upgrades']:
        data['prepare']['vehicle_upgrades'] = []
    if not data['prepare']['contact_accounts']:
        data['prepare']['contact_accounts'] = []
    return data

def pretty_get_cargo_details(data):
    # if data['company']:
    #     data['company'] = data['company'][0]
    if not data['contact_accounts']:
        data['contact_accounts'] = []
    if not data['goods_types']:
        data['goods_types'] = []
    if not data['vehicle_types']:
        data['vehicle_types'] = []
    if not data['vehicle_upgrades']:
        data['vehicle_upgrades'] = []
    if not data['load_unload']:
        data['load_unload'] = []
    return data

def pretty_get_cargo_list(data):
    for c in data:
        # c['company'] = c['company'][0]
        if not c['contact_accounts']:
            c['contact_accounts'] = []
        if not c['goods_types']:
            c['goods_types'] = []
        if not c['vehicle_types']:
            c['vehicle_types'] = []
        if not c['vehicle_upgrades']:
            c['vehicle_upgrades'] = []
        if not c['load_unload']:
            c['load_unload'] = []
    return data

def pretty_get_auctions(data):
    if data:
        data = data[0]
        # for a in data['auctions']:
        #     if a['account']:
        #         a['account'] = a['account'][0]
    return data
            

def pretty_get_loading_space_details(data):
    if data['vehicle_type']:
        data['vehicle_type'] = data['vehicle_type'][0]
    if data['company']:
        data['company'] = data['company'][0]
    if not data['vehicle_note']:
        data['vehicle_note'] = []
    if not data['contact_accounts']:
        data['contact_accounts'] = []
    if not data['vehicle_upgrades']:
        data['vehicle_upgrades'] = []
    if not data['starting_point_destination']:
        data['starting_point_destination'] = []


    return data

def pretty_get_loading_space_list(data):
    for l in data:
        if l['vehicle_type']:
            l['vehicle_type'] = l['vehicle_type'][0]
        if l['company']:
            l['company'] = l['company'][0]
        if not l['vehicle_note']:
            l['vehicle_note'] = []
        if not l['contact_accounts']:
            l['contact_accounts'] = []
        if not l['vehicle_upgrades']:
            l['vehicle_upgrades'] = []
        if not l['starting_point_destination']:
            l['starting_point_destination'] = []

    return data

def pretty_get_stock_list(data):
    for l in data:
        if l['company']:
            l['company'] = l['company'][0]
    return data

def pretty_get_stock_details(data):
    if data['company']:
        data['company'] = data['company'][0]

    return data

def pretty_get_company_details(data):
    if not data['company_emails']:
        data['company_emails'] = []
    if not data['company_numbers']:
        data['company_numbers'] = []
    return data