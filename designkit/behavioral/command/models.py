
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class ProcessMetadata:
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool
    result: Any | None = None
    exception: Exception | None = None
