SUPPORT_MAIL = 'info@joker-transport.com'
SUPPORT_PHONE_NUMBER = ''
APP_HREF = 'https://joker-transport.com'
APP_LINK = 'https://joker-transport.com'

ACTIVE = 'active'
NEED_CONFIRM = 'need_confirm'
REJECTED = 'rejected'
DEACTIVATE = 'deactivate'
UNAUTHORIZED = 'unauthorized'

HR = 'hr'
EN = 'en'

def get_footer(lang):
    if lang == HR:
        msg = f"""
            <br/>
            <p style="font-size:16px">Ako imate nekih pitanja stojimo vam na raspolaganju.</p>
            <p style="font-size:16px">{SUPPORT_MAIL}</p>
            <p style="font-size:16px">{SUPPORT_PHONE_NUMBER}</p>
            <br/>
            <p style="font-size:16px">Vaš Transport tim</p>
        """
    else:
        msg = f"""
            <p style="font-size:16px">To access the Transportation app please follow this link <a href="{APP_HREF}">{APP_LINK}</a> </p>
            <br/>
            <p style="font-size:16px">We would like to hear from you in case you have any questions.</p>
            <p style="font-size:16px">{SUPPORT_MAIL}</p>
            <p style="font-size:16px">{SUPPORT_PHONE_NUMBER}</p>
            <br/>
            <p style="font-size:16px">Your Transport team</p>
        """
    return msg