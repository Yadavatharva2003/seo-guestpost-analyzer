# app/queue/enqueue.py

import json
import redis

QUEUE_NAME = "seo_queue"
redis_client = redis.Redis(host="localhost", port=6379, db=0)

def enqueue_urls(run_id: str, urls: list[str]) -> int:
    """
    Enqueue all URLs exactly once for the given run.
    Returns total count.
    """
    jobs = [
        json.dumps({
            "run_id": run_id,
            "url": url.strip()
        })
        for url in urls if url.strip()
    ]

    if not jobs:
        return 0

    # Use pipeline to avoid duplicates & speed batching
    pipe = redis_client.pipeline()

    for job in jobs:
        pipe.rpush(QUEUE_NAME, job)

    pipe.execute()

    return len(jobs)
