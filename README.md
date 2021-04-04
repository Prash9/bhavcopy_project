Prerequisite: Docker,Docker-compose and git
Step 1:
    Clone the git repo: https://github.com/Prash9/bhavcopy_project.git
Step 2:
    docker pull prash9/bhavcopyequity:latest
    or you can build the image with the same name using the Dockerfile
Step 3:
    docker-compose up -d

To populate data in redis, uncomment line 11 in scheduler.py and 
change date for which data is required
    scheduler.add_job(Equity().update_bhavcopy, 'cron',[datetime(2021,4,5)],minute='*/2')

Restart the django service as:
    docker-compose restart django

The data will be populated once the scheduler run after 2 minutes.
Once data is populated comment the line 11 and restart django service so that the 2min 
scheduler is deactivated