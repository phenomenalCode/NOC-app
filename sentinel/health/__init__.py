"""
sentinel.sh — entrypoint.
 
The whole chain, minimally alive:
    fake events  ->  every detection rule  ->  colored terminal output
                 \-> metrics counters (step 06) at http://localhost:9100/metrics
 
Run:  python -m sentinel.main    (from the project root, venv active)
Stop: Ctrl-C
"""
 
from sentinel import fake_source
from sentinel.detect import block_burst, new_device
from sentinel.health import metrics
from sentinel.output import terminal
 
 
# every rule that should see every event. add rule #3 here later —
# this is the only line that changes when you add a detection.
RULES = (
    block_burst.check,
    new_device.check,
)
 
 
def run():
    metrics.start()   # /metrics is now live at http://localhost:9100/metrics
    terminal._console.print(
        "[dim]sentinel.sh — watching (fake source). "
        "metrics at http://localhost:9100/metrics — Ctrl-C to stop.[/]\n"
    )
    for event in fake_source.stream_events():
        metrics.record_event(source="fake")
        for rule in RULES:
            status = rule(event)
            if status is not None:
                metrics.record_alert(status)
                terminal.show(status)
 
 
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nstopped.")