import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, db=0)

QUEUE_NAME = "seo_queue"


def enqueue_urls(run_id: str, urls: list[str]):
    """
    Enqueue a batch of URLs for a given run_id.
    """
    for url in urls:
        job = {
            "run_id": run_id,
            "url": url
        }
        redis_client.lpush(QUEUE_NAME, json.dumps(job))

    return True
