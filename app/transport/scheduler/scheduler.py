from apscheduler.schedulers.background import BackgroundScheduler
from .auction_scheduler import check_finished_auction

def start():
    print("Pokretanje Schedulera")
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_finished_auction, 'interval', seconds=15)
    scheduler.start()