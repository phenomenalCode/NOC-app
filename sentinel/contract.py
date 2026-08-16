from dataclasses import dataclass, asdict, field
from enum import Enum
from colorama import Fore
from datetime import datetime, timezone

class State(Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"
    

@dataclass
class Status:
    state: State
    reason: str
    detail: dict = field(default_factory=dict)

    def emit(self):
        result = asdict(self)
        result["state"] = self.state.value
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
        return result