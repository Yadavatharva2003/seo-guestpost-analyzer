from threading import Lock

_lock = Lock()

progress_state = {
    "total": 0,
    "completed": 0,
    "running": False
}

def reset_progress(total: int):
    with _lock:
        progress_state["total"] = total
        progress_state["completed"] = 0
        progress_state["running"] = True

def increment_progress():
    with _lock:
        progress_state["completed"] += 1

def finish_progress():
    with _lock:
        progress_state["running"] = False
