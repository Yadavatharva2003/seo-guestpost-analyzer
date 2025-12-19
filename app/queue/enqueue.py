import uuid
from redis import Redis
from rq import Queue
from app.workers.worker import process_domain

redis = Redis.from_url("redis://localhost:6379")
queue = Queue("seo_tasks", connection=redis)


def enqueue_urls(urls: list):
    run_id = str(uuid.uuid4())

    for url in urls:
        queue.enqueue(process_domain, url, run_id)

    return run_id
