from ..models import *
from datetime import datetime
import pytz
from django.db import connection
from push_notifications.push_transport import send_push_auction_finished

def check_finished_auction():
    print("Provjera zavrsenih aukcija...")
    finished_auctions = Cargo.objects.filter(auction=True, auction_notification_sent=False, auction_end_datetime__lt=datetime.now(tz=pytz.timezone('Europe/Zagreb')))
    print(finished_auctions)

    send_push_auction_finished(finished_auctions)
    finished_auctions.update(auction_notification_sent=True)
    # print("Queries Counted: {}".format(len(connection.queries)))