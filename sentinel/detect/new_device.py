"""
Detection rule — new_device (step 02, your hand-written one).

Fires AMBER the first time a client (by MAC) is seen that wasn't part of
the known baseline. Different pattern from block_burst:
    block_burst = "too much, too fast"  -> a time WINDOW (deque)
    new_device  = "never seen before"   -> long-term MEMORY (set)

Contract (same as every rule):  check(event) -> Status | None
    event is the raw dict from the source, e.g.
        {"client": "192.168.1.42", "mac": "a4:83:e7:2c:11:9f",
         "domain": "...", "blocked": False}

────────────────────────────────────────────────────────────────────
This file is YOURS to write. The rails are here; the three real
decisions are marked TODO. Fill them in, then run it against a fake
source that emits a `mac` field. Don't peek at block_burst for the
logic — the shape is the same, the thinking is not.
────────────────────────────────────────────────────────────────────
"""

from sentinel.contract import Status, State
from datetime import datetime, timezone

# ── tuning ──────────────────────────────────────────────────
# How many events to watch silently before we start alerting. During
# warm-up we LEARN the baseline; we don't cry "new!" at every device
# on the first run. (Later this moves to config/rules.yaml.)
WARMUP = 50


# ── state: everything we've ever seen, persists across calls ─
_seen: set[str] = set()
_events_seen: int = 0



def _is_locally_administered(mac: str) -> bool:
    """Bit 0x02 of the first octet is set on randomized / locally-assigned
    MACs — most modern phones do this for privacy. A cheap 'is this a
    real burned-in address or a throwaway?' signal."""
    try:
        return bool(int(mac.split(":")[0], 16) & 0b10)
    except (ValueError, IndexError):
        return False
 
   
    
    
def check(event: dict) -> Status | None:
    global _events_seen
    ip_address = event.get("ip")

    identity = event.get("mac")  
    if identity is None:
        return None
    
    is_known = identity in _seen

    _events_seen += 1
    _seen.add(identity)

    if _events_seen <= WARMUP:
        return None
    else:

        if is_known:
            return None

        now = datetime.now(timezone.utc) #This is the current time in UTC

        return Status(
                state= State.AMBER,
                reason=f"{identity} is not part of known baseline",
                detail={
                "rule":"new_device",
                "source":"pfsense",
                "ip":ip_address, # "192.168.20.9"
                "hour_of_day": now.hour,  # cheap "is this 3am" signal
                # "mac_vendor": vendor_lookup(identity),       # e.g. "Espressif Inc." — via OUI table/lib
                "hostname": event.get("hostname"),           # e.g. "iPhone-Carter", often None for IoT junk
                "dhcp_fingerprint": event.get("dhcp_fp"),    # option 55 param list, e.g. "1,121,3,6,15,119,252"
                "lease_time_s": event.get("lease_time"),   # e.g. 86400                      
                "vlan": event.get("vlan"),                   # 20
                "interface": event.get("interface"),         # "igb2" / "IOT-AP" / port name
                "wireless": event.get("wireless"), 
                "mac_randomized": _is_locally_administered(identity),           # True/False
             } )