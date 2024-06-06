import os
from django.core.mail import send_mail, get_connection
import after_response
from .constants import *


def get_message_lang(alpha2Code):
    return HR
    hr = ['BA', 'HR', 'ME', 'XK', 'RS']
    if alpha2Code in hr:
        return HR
    return EN

def get_title_message_activate(lang):
    if lang == HR:
        title = "Vaš račun je aktiviran"
        message = f"""
                        <html>
                        <head></head>
                        <body>
                            <p style="font-size:16px">Poštovani,</p>
                            <p style="font-size:16px">Vaš račun je aktiviran i spreman za upotrebu.</p>
                            <p style="font-size:16px">Aplikaciji Transport možete pristupiti na sljedećoj poveznici <a href="{APP_HREF}">{APP_LINK}</a> </p>
                            {get_footer(lang)}
                        </body>
                        </html>
                    """
    elif lang == EN:
        title = "Vaš račun je aktiviran"
        message = f"""
                                <html>
                                <head></head>
                                <body>
                                    <p style="font-size:16px">Poštovani,</p>
                                    <p style="font-size:16px">Vaš račun je aktiviran i spreman za upotrebu.</p>
                                    <p style="font-size:16px">Aplikaciji Transport možete pristupiti na sljedećoj poveznici <a href="{APP_HREF}">{APP_LINK}</a> </p>
                                    {get_footer(lang)}
                                </body>
                                </html>
                            """
    return title, message


def get_title_message_deactivate(lang):
    if lang == HR:
        title = "Deaktivacija računa"
        message = f"""
                        <html>
                        <head></head>
                        <body>
                            <p style="font-size:16px">Poštovani,</p>
                            <p style="font-size:16px">Vaš račun za aplikaciju Transport je deaktiviran.</p>
                            {get_footer(lang)}
                        </body>
                        </html>
                    """
    elif lang == EN:
        title = "Deaktivacija računa"
        message = f"""
                                <html>
                                <head></head>
                                <body>
                                    <p style="font-size:16px">Poštovani,</p>
                                    <p style="font-size:16px">Vaš račun za aplikaciju Transport je deaktiviran.</p>
                                    {get_footer(lang)}
                                </body>
                                </html>
                            """
    return title, message

def get_title_message_unauthorized(lang):
    if lang == HR:
        title = "Račun nije odobren"
        message = f"""
                        <html>
                        <head></head>
                        <body>
                            <p style="font-size:16px">Poštovani,</p>
                            <p style="font-size:16px">Vaš račun za aplikaciju Transport nije odobren.</p>
                            {get_footer(lang)}
                        </body>
                        </html>
                    """
    elif lang == EN:
        title = "Račun nije odobren"
        message = f"""
                                <html>
                                <head></head>
                                <body>
                                    <p style="font-size:16px">Poštovani,</p>
                                    <p style="font-size:16px">Vaš račun za aplikaciju Transport nije odobren.</p>
                                    {get_footer(lang)}
                                </body>
                                </html>
                            """
    return title, message

def get_message_by_confirmation_type(_type, company_country):
    if _type == ACTIVE:
        title, message = get_title_message_activate(get_message_lang(company_country))
    elif _type == DEACTIVATE:
        title, message = get_title_message_deactivate(get_message_lang(company_country))
    elif _type == UNAUTHORIZED:
        title, message = get_title_message_unauthorized(get_message_lang(company_country))
    return title, message

@after_response.enable
def send_company_confirmation_email(recipient, _type, company_id):
    from transport.models import Company
    try:

        # company = Company.objects.select_related('country').get(id=company_id)
        # company_country = company.country.alpha2Code
        company_country = HR

        print("Idemo poslat mail")
        EMAIL_HOST = os.environ.get("EMAIL_PASS_HOST")
        EMAIL_HOST_USER = os.environ.get("EMAIL_PASS_USER")
        EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASS_PASS")
        EMAIL_PORT = 465
        EMAIL_USE_TLS = False
        EMAIL_USE_SSL = True

        connection = get_connection(host=EMAIL_HOST,
                                    port=EMAIL_PORT,
                                    username=EMAIL_HOST_USER,
                                    password=EMAIL_HOST_PASSWORD,
                                    use_ssl=EMAIL_USE_SSL)

        title, message = get_message_by_confirmation_type(_type, get_message_lang(company_country))
        print("Slanje maila dobrodoslice...")
        send_mail(title, message, EMAIL_HOST_USER, [recipient], connection=connection, fail_silently=False, html_message=message)
        print("Poslano!")

    except Exception as e:
        print(str(e))
        pass