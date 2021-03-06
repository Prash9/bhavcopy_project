from datetime import datetime,timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .equity import Equity

def test():
    print("Scheduler beat...")

def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(test, 'interval', seconds=10)
    # scheduler.add_job(Equity().update_bhavcopy, 'cron',[datetime(2021,4,1)],minute='*/2')
    scheduler.add_job(Equity().update_bhavcopy, 'cron',[datetime.now()-timedelta(days=1)], day_of_week='mon-fri', hour='4',minute='30')
    scheduler.add_job(Equity().update_bhavcopy, 'cron',[datetime.now()],day_of_week='mon-fri', hour='12',minute='40')
    scheduler.start()