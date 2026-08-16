"""
Metrics — step 06.
 
Exposes Prometheus counters over HTTP so Prometheus can scrape them and
Grafana can chart them. This is the piece that reads as NOC monitoring.
 
Call start() once at boot, then record() on each event / alert.
Metrics live at  http://localhost:9100/metrics
"""
 
from prometheus_client import Counter, start_http_server
 
 
# how many raw events the analyzer has ingested, by source
EVENTS = Counter(
    "sentinel_events_total",
    "Events ingested by the analyzer",
    ["source"],
)
 
# how many alerts fired, split by which rule and what state
ALERTS = Counter(
    "sentinel_alerts_total",
    "Alerts emitted by detection rules",
    ["rule", "state"],
)
 
 
def start(port: int = 9100):
    """Start the /metrics HTTP endpoint. Call once at boot."""
    start_http_server(port)
 
 
def record_event(source: str = "fake"):
    EVENTS.labels(source=source).inc()
 
 
def record_alert(status):
    """Count an alert. Reads rule + state straight off the Status."""
    rule = status.detail.get("rule", "unknown")
    ALERTS.labels(rule=rule, state=status.state.value).inc()