from dataclasses import dataclass
from typing import Optional


MAX_OPERATIONS = 4


@dataclass
class MetricsTracker:
    session_id: Optional[int] = None
    read_count: int = 0
    write_count: int = 0
    retry_count: int = 0
    risk_score: int = 0

    def track_read(self):
        self.read_count += 1
        self._update_risk()

    def track_write(self):
        self.write_count += 1
        self._update_risk()

    def track_retry(self):
        self.retry_count += 1
        self._update_risk()

    def total_operations(self):
        return self.read_count + self.write_count

    def _update_risk(self):
        # Weighted risk formula
        self.risk_score = (
            (self.read_count * 1) +
            (self.write_count * 2) +
            (self.retry_count * 3)
        )

    def should_block(self):
        return self.total_operations() > MAX_OPERATIONS
