"""
Terminal output — step 03.

The dumbest possible face: print the status in colored text.
Reads only `state` and `reason`; `detail` rides along unused for now.
"""

from rich.console import Console

from sentinel.contract import State

_console = Console()

_COLOR = {
    State.GREEN: "green",
    State.AMBER: "yellow",
    State.RED: "red",
}


def show(status):
    """Print one status line: e.g.  RED  192.168.1.42 hit 12 blocked domains in 60s"""
    color = _COLOR[status.state]
    label = status.state.value.upper()
    _console.print(f"[bold {color}]{label:5}[/] {status.reason}")
