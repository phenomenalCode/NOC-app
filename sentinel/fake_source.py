"""
Fake event source — no hardware needed.
 
Emits a stream of network events with:
  - a `mac` field, so new_device has something to judge
  - a small pool of KNOWN devices (baseline)
  - the occasional BRAND-NEW device after warm-up, so new_device fires
  - the occasional burst of blocked lookups, so block_burst fires
 
Same shape a real pihole/pfsense reader will yield, so it's a drop-in swap.
"""
 
import random
import time
 
 
# known baseline devices — (client ip, mac)
KNOWN_DEVICES = [
    ("192.168.1.10", "b8:27:eb:01:02:03"),   # e.g. a Pi (burned-in MAC)
    ("192.168.1.42", "3c:22:fb:aa:bb:cc"),   # laptop
    ("192.168.1.77", "1c:36:bb:11:22:33"),   # tv
]
 
# pool of "new" devices that can wander in (randomized-looking MACs)
NEW_DEVICES = [
    ("192.168.1.120", "de:ad:be:ef:00:01"),
    ("192.168.1.121", "a6:11:22:33:44:55"),
    ("192.168.1.122", "fe:99:88:77:66:55"),
]
 
CLEAN_DOMAINS = ["github.com", "wikipedia.org", "netflix.com", "python.org"]
AD_DOMAINS = ["ads.doubleclick.net", "track.example.com",
              "telemetry.badvendor.io", "metrics.creepy.tv"]
 
_new_pool = list(NEW_DEVICES)   # devices that haven't appeared yet
 
 
def _event(client, mac, domain, blocked):
    return {"client": client, "mac": mac, "domain": domain, "blocked": blocked}
 
 
def stream_events(delay: float = 0.4):
    """Yield fake DNS events forever."""
    while True:
        roll = random.random()
 
        # ~8%: a brand-new device shows up (fires new_device after warm-up)
        if roll < 0.08 and _new_pool:
            client, mac = _new_pool.pop(random.randrange(len(_new_pool)))
            yield _event(client, mac, random.choice(CLEAN_DOMAINS), False)
 
        # ~15%: a known device goes on a blocked-domain spree (fires block_burst)
        elif roll < 0.23:
            client, mac = random.choice(KNOWN_DEVICES)
            for _ in range(random.randint(6, 14)):
                yield _event(client, mac, random.choice(AD_DOMAINS), True)
                time.sleep(delay / 3)
 
        # otherwise: normal allowed traffic from a known device
        else:
            client, mac = random.choice(KNOWN_DEVICES)
            yield _event(client, mac, random.choice(CLEAN_DOMAINS), False)
 
        time.sleep(delay)