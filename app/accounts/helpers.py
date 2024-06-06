import string
import random


def pretty_update_account_request_data(data):
    data['name'] = data['account_full_name']
    data['phone_number'] = data['account_phone_number']
    data['languages'] = data['account_languages']
    return data


def generate_random_account_password(str_size=6):
    """
    Generiranje random lozinke za korisnika
    """
    allowed_chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(allowed_chars) for x in range(str_size))
