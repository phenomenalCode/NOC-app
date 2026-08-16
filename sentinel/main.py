"""sentinel.sh entrypoint. fake events -> rules -> terminal + metrics."""

from sentinel import fake_source
from sentinel.detect import block_burst, new_device
from sentinel.health import metrics
from sentinel.output import terminal

RULES = (block_burst.check, new_device.check)


def run():
    metrics.start()
    terminal._console.print(
        "[dim]sentinel.sh watching. metrics at "
        "http://localhost:9100/metrics -- Ctrl-C to stop.[/]\n"
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
