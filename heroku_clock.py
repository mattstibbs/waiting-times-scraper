import schedule
import time
import redis
from rq import Queue

import check
import config
import probes

print(f"{len(probes.get_probe_list())} probes configured to run every {config.CHECK_RATE_MINUTES} minute(s)")

# Set up RQ queue
conn = redis.from_url(config.REDIS_URL)
q = Queue(connection=conn)


def add_job():
    probe_list = probes.get_probe_list()
    
    for probe in probe_list:
        print("Adding probe to queue")
        q.enqueue(check.job,
                  probe,
                  ttl=f'{config.CHECK_RATE_MINUTES}m')
    

schedule.every(config.CHECK_RATE_MINUTES).minutes.do(add_job)

add_job()

while True:
    print(f"Ping!")
    schedule.run_pending()
    time.sleep(60)
