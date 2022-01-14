import multiprocessing
import os

# Grab the number of desired workers from the environment or use Ncpu * 2 + 1
workers = os.environ.get(
    "GUNICORN_NB_WORKERS",
    multiprocessing.cpu_count() * 2 + 1,
)
# worker_class = 'gevent'

max_requests = 400
timeout = 30
keep_alive = 2

preload = True
