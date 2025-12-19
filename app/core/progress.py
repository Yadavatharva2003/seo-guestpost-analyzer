from threading import Lock

_lock = Lock()

# track progress per run_id
progress = {}   # { run_id: { total, completed } }


def set_run_progress(run_id: str, completed: int, total: int):
    with _lock:
        progress[run_id] = {
            "total": total,
            "completed": completed
        }


def increment_progress(run_id: str):
    with _lock:
        if run_id in progress:
            progress[run_id]["completed"] += 1


def get_run_progress(run_id: str):
    with _lock:
        if run_id not in progress:
            return {"total": 0, "completed": 0}

        return {
            "total": progress[run_id]["total"],
            "completed": progress[run_id]["completed"]
        }
