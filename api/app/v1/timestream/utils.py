
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple


def parse_timestream_datetime(timestream_datetime: str) -> datetime:
    return datetime.fromisoformat(f"{timestream_datetime[:-3]}+00:00")


def generate_intervals(period_start: datetime, period_end: datetime, step: relativedelta) -> List[Tuple[datetime, datetime]]:
    intervals = []
    i = 1
    current_interval = (period_start, period_start + step - timedelta(microseconds=1))
    while current_interval[1] < period_end:
        intervals.append(current_interval)
        current_interval = (
            period_start + step * i,
            period_start + step * (i + 1) - timedelta(microseconds=1)
        )
        i += 1
    intervals.append((current_interval[0], period_end))
    return intervals
