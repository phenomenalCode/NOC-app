sentinel.sh — home-lab network detection & monitoring

A small, always-on network monitor for a home lab. It ingests DNS/firewall events, runs stateful detection rules over them, and surfaces every decision as a single traffic-light object — green / amber / red — that any "face" (terminal today; web dashboard and a glowing desk mascot later) can subscribe to without knowing anything about how the decision was made.

The whole system is instrumented with Prometheus metrics on a /metrics endpoint, so throughput and alert rates are observable the way a production service would be.

Built as a CLI-first vertical slice: a real, working detection pipeline you can run in one command, designed so real log sources, a web dashboard, and an LLM analyst plug into the same contract later without the core changing. Full 00–08 roadmap lives in the design docs in the project root.

What it catches

Point it at a home network running Pi-hole and/or pfSense and it answers "is anything weird happening right now?" without hand-watching logs. Two threats it detects first:

A device suddenly hammers blocked ad/tracker domains — malware, a misbehaving smart-TV, or a compromised IoT device beaconing out.
A brand-new device joins the network that was never in the learned baseline — a guest, or someone on the Wi-Fi who shouldn't be.

The design goal is a decoupled brain: detection logic never talks to a terminal, a website, or an LED ring directly — everything reads the same Status object, so faces are added or removed without touching the core.

Architecture
  fake_source.stream_events()            RULES = (block_burst, new_device)
  ┌──────────────────────────┐           ┌────────────────────────────────┐
  │ yields network events     │  event    │ block_burst → windowed deque   │
  │ {client, mac, domain,     │ ────────► │ new_device  → baseline set     │
  │  blocked}                 │           └───────────────┬────────────────┘
  └──────────────────────────┘                           │ Status | None
                │ every event                             ▼
                ▼                              ┌────────────────────────┐
      ┌──────────────────────┐   record_alert │ contract.py — Status   │
      │  health/metrics.py    │◄──────────────│ {state, reason, detail}│
      │  Prometheus counters  │               └───────────┬────────────┘
      └──────────┬───────────┘                            │
                 ▼                        ┌────────────────┴────────────┐
     /metrics  :9100  (scrape target)     ▼                             ▼
                                ┌────────────────────┐       (planned: websocket
                                │  terminal.show()   │        → web dashboard,
                                │  rich colored line │        → net-spirit mascot)
                                └────────────────────┘

Live in main.py: fake_source → [block_burst, new_device] → terminal, with every event and alert recorded to Prometheus counters.

Screenshots
<!-- Add two images to a docs/ folder and update these paths -->

Detection running — RED bursts from block_burst, AMBER from new_device:

Show Image

Metrics endpoint — sentinel_* counters exposed for Prometheus at :9100/metrics:

Show Image

The contract — one object everything hangs off

contract.py is the spine. Every rule returns either None (nothing to report) or a Status:

python
class State(Enum):
    GREEN = "green"; AMBER = "amber"; RED = "red"

@dataclass
class Status:
    state: State
    reason: str
    detail: dict = field(default_factory=dict)

    def emit(self) -> dict:   # State -> its .value, plus a UTC timestamp
        ...

Because every consumer — terminal.py, the metrics recorder, and eventually a websocket server — only reads state / reason / detail, a new detection rule or a new output face drops in without touching anything else. Fixing this shape before writing any detection logic is the whole point.

Detection rules — two patterns, two questions
detect/block_burst.py — "too much, too fast"
State: dict[client] -> deque[timestamp], one sliding window per client.
On each blocked event: push time.time(), then pop from the left while the oldest entry is older than WINDOW (60s).
If what remains is >= LIMIT (5), fire State.RED.
Non-blocked events return None immediately.
State is module-level (_hits), persisting for the process's life — no DB.
detect/new_device.py — "never seen before"
State: set[str] of every MAC ever seen (_seen) plus an event counter.
Warm-up (WARMUP = 50 events): the rule records every MAC but never alerts — otherwise the first run would flag every device at once. This is a baseline-learning pattern, distinct from block_burst's time-windowed one.
After warm-up: an unseen MAC fires State.AMBER with a rich detail payload (IP, hostname, DHCP fingerprint, VLAN, interface, wireless flag, and whether the MAC looks randomized).
is_locally_administered(mac) checks bit 0x02 of the first octet — the bit set on privacy-randomized MACs (most modern phones) — a cheap "burned-in vendor address vs. throwaway" signal used in real network fingerprinting.
No mac field → returns None; it can't judge what it can't identify.

Both rules are registered in one tuple in main.py, so adding a third rule is a single line and the per-event dispatch loop never changes.

Observability

health/metrics.py exposes Prometheus counters over HTTP so the pipeline is monitorable like a production service:

sentinel_events_total{source} — ingest throughput, labeled by source so multiple feeds (Pi-hole, pfSense) can be measured independently.
sentinel_alerts_total{rule, state} — alerts, labeled by rule and state, so one metric answers "reds from block_burst?", "ambers from new_device?", and "total alerts" by filtering labels.

The library also auto-exposes process health (GC, memory, Python version) on the same endpoint. Prometheus scrapes http://localhost:9100/metrics; Grafana dashboards on top are the next step.

File map
File	Role	Status
contract.py	State enum + Status dataclass — the shared contract	
fake_source.py	Synthetic event generator (known devices, blocked bursts, new devices) standing in for a real reader	
main.py	Entrypoint — wires source → rules → terminal + metrics	
detect/block_burst.py	Rule: too many blocked lookups from one client too fast	
detect/new_device.py	Rule: a MAC never seen in the baseline appears	
output/terminal.py	Prints a Status as one colored line via rich	
health/metrics.py	Prometheus counters + /metrics endpoint	
tests/test_block_burst.py	Unit tests: firing, warm-up, window pruning, per-client isolation, serialization	

Reserved stubs for later steps: bus.py (asyncio.Queue to decouple ingest/detect/output into concurrent stages), ingest/pihole.py + ingest/pfsense.py (real log sources), output/server.py (FastAPI websocket for a web/mascot face), detect/base.py + ingest/base.py (formal interfaces).

Tools
Library	Where	Why
rich	output/terminal.py	Colored console now; grows into a live table later without a rewrite
prometheus-client	health/metrics.py	Labeled counters over a /metrics HTTP endpoint
pytest	tests/	Rule unit tests, including clock-controlled window pruning
Python standard library	everywhere else	dataclasses, enum, datetime, collections.deque/defaultdict, time — the core loop needs almost no third-party code

requirements.txt lists the full planned stack (FastAPI/uvicorn for the web face, PyYAML/APScheduler for config + scheduling, psutil/httpx for service health, ollama for the LLM analyst) commented out until each step is reached.

Concepts exercised
Contract-first design — locking the Status shape before writing any detection logic, so every consumer swaps independently of the brain.
Generators as an event stream — stream_events() is an infinite yield-based generator; a real ingest/pihole.py can later yield the same shape from a SQLite tail, and nothing downstream changes.
Two state-tracking shapes for two questions — a time-boxed deque (block_burst) vs. long-term set membership (new_device).
Warm-up / baseline-learning — you can't say "this is new" without first silently building what "known" means; alerting during warm-up is noise.
Application metrics with labels — few Prometheus counters, rich labels (source / rule / state), so queries slice the same metric many ways.
Bit-level MAC inspection — the 0x02 locally-administered bit to detect randomized MACs, a real network-fingerprinting technique.
Dataclasses + enums over loose dicts/strings — free __repr__/equality, a closed set of states, and asdict() for the plain-dict output boundary.
Return-None-early — rules bail fast when an event lacks what they need, keeping the "nothing to report" path cheap and explicit.
Running it
bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m sentinel.main                              # Ctrl-C to stop

This runs the live loop — fake_source → [block_burst, new_device] → terminal — and serves metrics at http://localhost:9100/metrics (open it in a browser and search for sentinel_; the counters climb as events flow).

Run the tests:

bash
pytest -v
Roadmap

The CLI slice is complete; the system is built so each next layer plugs into the existing contract:

Real log sources — ingest/pihole.py (tail the FTL SQLite DB) and ingest/pfsense.py (syslog listener) replace fake_source, yielding the same event shape.
Grafana dashboards — on top of the metrics already exposed.
Concurrent pipeline — bus.py as an asyncio.Queue so ingest, detect, and serve run as decoupled stages.
Web dashboard — output/server.py (FastAPI websocket) broadcasting the same Status to a React front-end.