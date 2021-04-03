from apscheduler.schedulers.background import BackgroundScheduler
from .equity import Equity

def test():
    print("ASDKLASJDKLASDJLKA")

def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(test, 'interval', seconds=10)
    # scheduler.add_job(Equity().update_bhavcopy, 'cron',minute='*/2')
    scheduler.add_job(Equity().update_bhavcopy, 'cron', day_of_week='mon-fri', hour='18',minute='10')
    scheduler.start()