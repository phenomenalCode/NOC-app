"""
Detection rule — block_burst (steps 02).
 
Fires when a single client racks up too many BLOCKED lookups inside a
short window. The rule owns its own state: a per-client deque of
timestamps that it prunes to the window on every event.
 
Contract: check(event) -> Status | None
    event is the raw dict from the source, e.g.
        {"client": "192.168.1.42", "domain": "...", "blocked": True}
    Returns a Status when the threshold is crossed, else None.
"""
 
import time
from collections import defaultdict, deque
 
from sentinel.contract import Status, State
 
 
# --- tuning (later these move to config/rules.yaml, step 05) ---
WINDOW = 60     # seconds to look back
LIMIT = 5       # blocked hits within WINDOW that trips the alert
 
# --- state: one timestamp deque per client, persists across calls ---
_hits: dict[str, deque] = defaultdict(deque)
 
 
def check(event: dict) -> Status | None:
    # only blocked lookups count toward a burst
    if not event.get("blocked"):
        return None
 
    client = event["client"]
    now = time.time()
 
    window = _hits[client]
    window.append(now)
 
    # drop anything older than WINDOW seconds off the left
    while window and now - window[0] > WINDOW:
        window.popleft()
 
    count = len(window)
    if count < LIMIT:
        return None
 
    # threshold crossed -> emit a Status
    return Status(
        state=State.RED,
        reason=f"{client} hit {count} blocked domains in {WINDOW}s",
        detail={
            "rule": "block_burst",
            "source": "pihole",
            "client": client,
            "count": count,
            "threshold": LIMIT,
            "window_s": WINDOW,
            "sample": [event["domain"]],
        },
    )
 