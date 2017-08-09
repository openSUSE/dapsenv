import time
import job
import const
import logging
import logging.config
import random
logging.getLogger().addHandler(logging.NullHandler())
logging.config.dictConfig(const.DEFAULT_LOGGING_DICT)
log = logging.getLogger('test')


jq = job.JobQueue(7)

for i in range(0, 100):
    sec = random.randint(1, 10)
    cmd = 'sleep {}'.format(sec)
    jq.push(job.Build(i, i, cmd), random.randint(1, 100))

while True:
    jq.log_info()
    jq.run()
    time.sleep(2)
