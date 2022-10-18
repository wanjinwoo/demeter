from dataclasses import dataclass
from datetime import datetime, timedelta

from demeter._typing import RowData, ZelosError


class Trigger:
    def __init__(self, do=None):
        self._do = do if do is not None else self.do_nothing

    def when(self, row_data: RowData) -> bool:
        return False

    def do_nothing(self, row_data: RowData):
        pass

    def do(self, row_data: RowData):
        return self._do(row_data)


class AtTimeTrigger(Trigger):
    def __init__(self, time: datetime, do=None):
        self._time = time
        super().__init__(do)

    def when(self, row_data: RowData) -> bool:
        return row_data.timestamp == self._time


class AtTimesTrigger(Trigger):
    def __init__(self, time: [datetime], do=None):
        self._time = time
        super().__init__(do)

    def when(self, row_data: RowData) -> bool:
        return self._time in row_data.timestamp


@dataclass
class TimeRange:
    start: datetime
    end: datetime


class TimeRangeTrigger(Trigger):
    def __init__(self, time_range: TimeRange, do=None):
        self._time_range = time_range
        super().__init__(do)

    def when(self, row_data: RowData) -> bool:
        return self._time_range.start <= row_data.timestamp < self._time_range.end


class TimeRangesTrigger(Trigger):
    def __init__(self, time_range: [TimeRange], do=None):
        self._time_range: [TimeRange] = time_range
        super().__init__(do)

    def when(self, row_data: RowData) -> bool:
        for r in self._time_range:
            if r.start <= row_data.timestamp < r.end:
                return True
        return False


def check_time_delta(delta: timedelta):
    if delta.total_seconds() % 60 != 0:
        raise ZelosError("min time span is 1 minute")


class PeriodTrigger(Trigger):
    def __init__(self, time_delta: timedelta, do=None, trigger_immediately=False):
        self._next_match = None
        self._delta = time_delta
        self._trigger_immediately = trigger_immediately
        check_time_delta(time_delta)
        super().__init__(do)

    def reset(self):
        self._next_match = None

    def when(self, row_data: RowData) -> bool:
        if self._next_match is None:
            self._next_match = row_data.timestamp + self._delta
            return self._trigger_immediately

        if self._next_match == row_data.timestamp:
            self._next_match = self._next_match + self._delta
            return True

        return False


class PeriodsTrigger(Trigger):
    def __init__(self, time_delta: [timedelta], do=None, trigger_immediately=False):
        self._next_matches = [None for _ in time_delta]
        self._deltas = time_delta
        self._trigger_immediately = trigger_immediately

        for td in time_delta:
            check_time_delta(td)
        super().__init__(do)

    def reset(self):
        self._next_matches = [None for _ in self._delta]

    def when(self, row_data: RowData) -> bool:
        if self._next_matches[0] is None:
            self._next_matches = [row_data.timestamp + d for d in self._delta]
            return self._trigger_immediately

        for i in range(len(self._deltas)):
            if self._next_matches[i] == row_data.timestamp:
                self._next_matches[i] = self._next_matches[i] + self._deltas[i]
                return True

        return False
