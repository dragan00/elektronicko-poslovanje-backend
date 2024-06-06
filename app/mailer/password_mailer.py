import os
from django.core.mail import send_mail, get_connection
import after_response

HR = 'HR'
EN = 'EN'

def get_message_lang(alpha2Code):
    hr = ['BA', 'HR', 'ME', 'XK', 'RS']
    if alpha2Code in hr:
        return HR
    return EN

def get_title_message(lang, email, password):
    support_mail = 'support@test.com'
    support_phone_number = '+387 63 355 585'
    if lang == HR:
        title = "Potvrda o registraciji"
        message = f"""
                        <html>
                        <head></head>
                        <body>
                            <p style="font-size:16px">Obavještavamo vas da vam je otvoren račun u aplikaciji Transport.</p>
                            <p style="font-size:16px">Vaši podaci za prijavu su:</p>
                            <p style="font-size:16px">Korisničko ime: <b>{email}</b></p>
                            <p style="font-size:16px">Lozinka: <b>{password}</b></p>
                            <p style="font-size:16px">Aplikaciji Transport možete pristupiti na sljedećoj poveznici <a href="http://transporti.ga">www.transporti.ga</a> </p>
                            <br/>
                            <p style="font-size:16px">Ako imate nekih pitanja stojimo vam na raspolaganju.</p>
                            <p style="font-size:16px">{support_mail}</p>
                            <p style="font-size:16px">{support_phone_number}</p>
                            <br/>
                            <p style="font-size:16px">Vaš Transport tim</p>
                        </body>
                        </html>
                    """
    elif lang == EN:
        title = "Confirmation of registration"
        message = f"""
                    <html>
                    <head></head>
                    <body>
                        <p style="font-size:16px">Congratulations!</p>
                        <p style="font-size:16px">We have your account in Transporation app opened and ready for use.</p>
                        <p style="font-size:16px">Your login credentials:</p>
                        <p style="font-size:16px">Username: <b>{email}</b></p>
                        <p style="font-size:16px">Password: <b>{password}</b></p>
                        <p style="font-size:16px">To access the Transportation app please follow this link <a href="http://transporti.ga">www.transporti.ga</a> </p>
                        <br/>
                        <p style="font-size:16px">We would like to hear from you in case you have any questions.</p>
                        <p style="font-size:16px">{support_mail}</p>
                        <p style="font-size:16px">{support_phone_number}</p>
                        <br/>
                        <p style="font-size:16px">Your Transport team</p>
                    </body>
                    </html>
                """
    return title, message

@after_response.enable
def send_account_password_email(email, password, company_id):
    from transport.models import Company
    try:

        company = Company.objects.select_related('country').get(id=company_id)
        company_country = company.country.alpha2Code

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

        title, message = get_title_message(get_message_lang(company_country), email, password)
        print("Slanje maila dobrodoslice...")
        send_mail(title, message, EMAIL_HOST_USER, [email], connection=connection, fail_silently=False, html_message=message)
        print("Poslano!")

    except Exception as e:
        print(str(e))
        pass