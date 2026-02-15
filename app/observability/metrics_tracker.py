from dataclasses import dataclass
from typing import Optional


MAX_OPERATIONS = 4


@dataclass
class MetricsTracker:
    session_id: Optional[int] = None
    read_count: int = 0
    write_count: int = 0
    retry_count: int = 0
    high_risk: bool = False

    def track_read(self):
        self.read_count += 1
        self._evaluate_risk()

    def track_write(self):
        self.write_count += 1
        self._evaluate_risk()

    def track_retry(self):
        self.retry_count += 1

    def total_operations(self):
        return self.read_count + self.write_count

    def _evaluate_risk(self):
        if self.total_operations() > MAX_OPERATIONS:
            self.high_risk = True

    def should_block(self):
        return self.high_risk
