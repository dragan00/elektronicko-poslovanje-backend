from fcm_django.models import FCMDevice

def send_push_notification(account_ids, title, body, *args, **kwargs):
    print("Dohvatanje korisnika za slanje obavijesti...")
    device = FCMDevice.objects.filter(user_id__in=account_ids)
    for d in device:
        print(d.registration_id)
    print(device)
    print("Slanje obavijesti...")
    device.send_message(title, body, *args, **kwargs)
    print("Obavijest poslana")