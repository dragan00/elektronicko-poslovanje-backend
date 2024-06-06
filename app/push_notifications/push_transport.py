import os

from .push_notification_sender import *
import after_response
from transport.models import Cargo, Auction, CargoLoadUnload, LoadingSpace, StartingPointDestination
from accounts.models import Account
from django.db.models import Q
from transport.constants import LOAD, UNLOAD, STARTING, DESTINATION

def get_cargo_info_notification_body(cargo):
    try:
        load = CargoLoadUnload.objects.filter(cargo_id=cargo.id, type=LOAD).select_related('country', 'city').order_by('id')[0]
    except:
        load = None
    try:
        unload = CargoLoadUnload.objects.filter(cargo_id=cargo.id, type=UNLOAD).select_related('country', 'city').order_by('-id')[0]
    except:
        unload = None
    load_msg = ""
    unload_msg = ""
    if load:
        if load.city and load.country:
            load_msg = f"Utovar: {load.city.name}, {load.country.alpha2Code}"
        else:
            if load.country:
                load_msg = f"Utovar: {load.country.alpha2Code}"
            else:
                load_msg = f"Utovar: {load.city.name}"

    if unload:
        if unload.city and unload.country:
            unload_msg = f"Istovar: {unload.city.name}, {unload.country.alpha2Code}"
        else:
            if unload.country:
                unload_msg = f"Istovar: {unload.country.alpha2Code}"
            else:
                unload_msg = f"Istovar: {unload.city.name}"

    return load_msg + ' - ' + unload_msg

def get_loading_space_info_notification_body(ls):
    try:
        load = StartingPointDestination.objects.filter(loading_space_id=ls.id, type=STARTING).select_related('country', 'city').order_by('id')[0]
    except:
        load = None
    try:
        unload = StartingPointDestination.objects.filter(loading_space_id=ls.id, type=DESTINATION).select_related('country', 'city').order_by('-id')[0]
    except:
        unload = None
    load_msg = ""
    unload_msg = ""
    if load:
        if load.city and load.country:
            load_msg = f"Polazište: {load.city.name}, {load.country.alpha2Code}"
        else:
            if load.country:
                load_msg = f"Polazište: {load.country.alpha2Code}"
            else:
                load_msg = f"Polazište: {load.city.name}"

    if unload:
        if unload.city and unload.country:
            unload_msg = f"Odredište: {unload.city.name}, {unload.country.alpha2Code}"
        else:
            if unload.country:
                unload_msg = f"Odredište: {unload.country.alpha2Code}"
            else:
                unload_msg = f"Odredište: {unload.city.name}"

    return load_msg + ' - ' + unload_msg

@after_response.enable
def send_push_insert_auction(cargo_id, token):
    """
    cargo_id -> ID tereta za koji je dodana aukcija
    token -> Token od korisnika koji je dao aukciju
    """
    user_ids_to_send = []

    cargo = Cargo.objects.get(id=cargo_id)
    user_ids_to_send.append(cargo.created_by_id)

    try:
        auction = Auction.objects.filter(Q(cargo_id=cargo.id) & ~Q(account_id=cargo.created_by_id) & ~Q(account__auth_token=token)).order_by('-id')[0]
        user_ids_to_send.append(auction.account_id)
        print(auction)
    except:
        print("Nema ostalih aukcija")
        pass
    print(cargo)

    body = get_cargo_info_notification_body(cargo)
    send_push_notification(user_ids_to_send, "Dodana je nova ponuda", body, click_action=f"{os.environ.get('FRONTEND_URL')}/cargo/{cargo.id}")


@after_response.enable
def send_push_auction_finished(cargos):
    print("send_push_auction_finished pocetak")
    print(cargos)
    user_ids_to_send = []
    best_bid_title = "Vaša ponuda je najbolja"

    for c in cargos:
        print("Prolaz kroj teret")
        a = c.get_last_bid()
        if not a:
            print("Nije bila niti jedna aukcija")
            title = "Završena aukcija bez ponude"
            body = get_cargo_info_notification_body(c)
            send_push_notification([c.created_by_id], title, body, click_action=f"{os.environ.get('FRONTEND_URL')}/cargo/{c.id}")
        else:
            best_bid_body = get_cargo_info_notification_body(c)
            send_push_notification([a.account_id], best_bid_title, best_bid_body, click_action=f"{os.environ.get('FRONTEND_URL')}/cargo/{c.id}")
            creator_title = "Aukcija završena"
            creator_body = best_bid_body
            send_push_notification([c.created_by_id], creator_title, creator_body, click_action=f"{os.environ.get('FRONTEND_URL')}/cargo/{c.id}")

def get_ad_data_to_filter(data, type='c'):

    # data = {"load_unload":[{"country":9,"city":239,"zip_code":4122,"from_date":"","to_date":"","from_time":"","to_time":"","type":"unload","start_datetime":None,"end_datetime":None},{"country":4,"city":2758,"zip_code":51915,"place":None,"from_date":"","to_date":"","from_time":"","to_time":"","type":"unload","start_datetime":None,"end_datetime":None},{"country":7,"city":5379,"zip_code":58938,"place":None,"from_date":"2021-09-17T16:07:34.539Z","to_date":"","from_time":"","to_time":"","type":"load","start_datetime":"2021-09-17 06:07","end_datetime":None}],"cargo":{"goods_types":[8],"cargo_note":[{"lang":"hr","cargo_note":""},{"lang":"en","cargo_note":""},{"lang":"de","cargo_note":""}],"length":13.6,"width":2.4,"weight":24,"price":560,"exchange":False},"vehicle":{"vehicle_types":[5],"vehicle_upgrades":[],"vehicle_equipment":[],"contact_accounts":[1],"vehicle_note":[{"lang":"hr","vehicle_note":""},{"lang":"en","vehicle_note":""},{"lang":"de","vehicle_note":""}]},"auction":{"auction":False,"start_price":None,"min_down_bind_percentage":None,"auction_end_datetime":None}}

    filters = {
        "from": [],
        "to": [],
        "vehicle_types": [],
        "vehicle_equipment": [],
        "vehicle_upgrades": []
    }



    if type == 'c':
        for i in data['load_unload']:
            if i['type'] == LOAD:
                filters['from'].append({
                    "country": i['country'],
                    "city": i['city'],
                    "zip_code": i['zip_code']
                })
            elif i['type'] == UNLOAD:
                filters['to'].append({
                    "country": i['country'],
                    "city": i['city'],
                    "zip_code": i['zip_code']
                })
        if 'vehicle_types' in data['vehicle'] and data['vehicle']['vehicle_types']:
            filters['vehicle_types'] = data['vehicle']['vehicle_types']
    else:
        for i in data['starting_point_destination']:
            if i['type'] == STARTING:
                filters['from'].append({
                    "country": i['country'],
                    "city": i['city'],
                    "zip_code": i['zip_code']
                })
            elif i['type'] == DESTINATION:
                filters['to'].append({
                    "country": i['country'],
                    "city": i['city'],
                    "zip_code": i['zip_code']
                })
        if 'vehicle_type' in data['vehicle'] and data['vehicle']['vehicle_type']:
            filters['vehicle_types'] = [data['vehicle']['vehicle_type']]


    if 'vehicle_upgrades' in data['vehicle'] and data['vehicle']['vehicle_upgrades']:
        filters['vehicle_upgrades'] = data['vehicle']['vehicle_upgrades']

    if 'vehicle_equipment' in data['vehicle'] and data['vehicle']['vehicle_equipment']:
        filters['vehicle_equipment'] = data['vehicle']['vehicle_equipment']

    return filters

def get_place_type(place):
    t = 0
    if place['country']:
        t = 1
        if place['city']:
            t = 2
            if place['zip_code']:
                t = 3
    return t

def check_matching_places(ad_places, user_places):
    """
    Types: 1 - Drzava, 2 - Grad, 3 - Postanski broj
    """
    print("AD PLACES")
    print(ad_places)
    print("USER PLACES")
    print(user_places)
    for up in user_places:
        t = get_place_type(up)
        print(f"TYPE {t}")
        if t == 1:
            #Samo drzave
            find = list(filter(lambda place: place['country'] == up['country']['id'], ad_places))
            if find:
                print("Pronaden")
                return True
        elif t == 2:
            #Samo gradove
            find = list(filter(lambda place: place['city'] == up['city']['id'], ad_places))
            if find:
                print("Pronaden")
                return True
        elif t == 3:
            #Samo Zip
            find = list(filter(lambda place: place['zip_code'] == up['zip_code']['id'], ad_places))
            if find:
                print("Pronaden")
                return True
    return False

def check_filter_list(ad_list, user_list):
    """
    ad_list -> Lista ID-ova od oglasa
    user_list -> Lista ID-ova iz korisnikova filtera
    Ako se ijedan korisnikov id nalazi u oglasnoj listi vraca TRUE
    """
    for ul in user_list:
        if ul in ad_list:
            return True
    return False

def is_user_pane_valid(p):
    print(p)
    if 'from' in p and p['from']:
        return True
    if 'to' in p and p['to']:
        return True
    if 'vehicle' in p:
        _p = p['vehicle']
        if 'type' in _p and _p['type']:
            return True
        if 'upgrades' in _p and _p['upgrades']:
            return True
        if 'equipment' in _p and _p['equipment']:
            return True
    return False

def check_user_filter_for_ad(panes, cargo_filter_data, type='c'):
    """
    panes -> Korisnikovi filteri
    cargo_filter_data -> Podaci koji se filtriraju od oglasa
    """
    if type == 'c':
        p_cargo = panes['cargo']
    else:
        p_cargo = panes['loadingSpace']
    print(len(p_cargo))
    send_push = False
    valid_panes = []
    for p in p_cargo:
        p = p['filters']
        if is_user_pane_valid(p):
            print("Validan je pane")
            valid_panes.append(p)
        else:
            print("Nije validan pane")

    if not valid_panes:
        return False

    for p in valid_panes:
        from_find = True
        to_find = True
        v_type = True
        v_upgrades = True
        v_equipment = True
        if 'from' in p and p['from']:
            from_find = False
            if check_matching_places(cargo_filter_data['from'], p['from']):
                from_find = True
            else:
                continue

        if 'to' in p and p['to']:
            to_find = False
            if check_matching_places(cargo_filter_data['to'], p['to']):
                to_find = True
            else:
                continue

        if 'vehicle' in p:
            _p = p['vehicle']
            if 'type' in _p and _p['type']:
                v_type = False
                if check_filter_list(cargo_filter_data['vehicle_types'], _p['type']):
                    v_type = True
                else:
                    continue

            if 'upgrades' in _p and _p['upgrades']:
                v_upgrades = False
                if check_filter_list(cargo_filter_data['vehicle_upgrades'], _p['upgrades']):
                    v_upgrades = True
                else:
                    continue

            if 'equipment' in _p and _p['equipment']:
                v_equipment = False
                if check_filter_list(cargo_filter_data['vehicle_equipment'], _p['equipment']):
                    v_equipment = True
                else:
                    continue


        if from_find and to_find and v_type and v_upgrades and v_equipment:
            return True

        print("From find")
        print(from_find)
        print("To find")
        print(to_find)
        print("V type")
        print(v_type)
        print("v_equip")
        print(v_equipment)
        print("v_upg")
        print(v_upgrades)

    return False

@after_response.enable
def send_push_notification_by_user_filter(insert_data, id, type='c', exclude_ids=[]):
    """
    type = c - cargo | l - loading space
    """
    users = Account.objects.filter(Q(is_active=True) & ~Q(panes=None) & ~Q(id__in=exclude_ids))

    #filter_data -> Podacij koji se mogu filtrirat za teret ili utovarni prostor
    filter_data = get_ad_data_to_filter(insert_data, type)

    users_to_send = []

    for user in users:
        p = user.panes
        print(p)
        if check_user_filter_for_ad(p, filter_data, type):
            print("Treba poslat obavijest korisniku")
            users_to_send.append(user.id)
        else:
            print("Ne treba poslat obavijest")
        print(user)
    print(users_to_send)
    if type == 'c':
        if users_to_send:
            cargo = Cargo.objects.get(id=id)
            body = "Mogao bi vas zanimati ovaj oglas | " + get_cargo_info_notification_body(cargo)
            send_push_notification(users_to_send, "Novi oglas za teret", body)
            # send_push_notification(users_to_send, "Novi oglas za teret", body,
            #                        click_action=f"{os.environ.get('FRONTEND_URL')}/cargo/{cargo.id}")
    else:
        loading_space = LoadingSpace.objects.get(id=id)
        print(loading_space)
        body = "Moga bi vas zanimati ovaj oglas | " + get_loading_space_info_notification_body(loading_space)
        send_push_notification(users_to_send, "Novi oglas za utovarni prostor", body)
        # send_push_notification(users_to_send, "Novi oglas za utovarni prostor", body,
        #                        click_action=f"{os.environ.get('FRONTEND_URL')}/loadingspace/{loading_space.id}")
    return filter_data