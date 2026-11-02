from collections import deque
from time import perf_counter


class Profiler:

    def __init__(self, history_size=120):
        self.enabled = True

        self.history = deque(
            maxlen=history_size
        )

        self.current_sample = {}

    def begin_sample(self):
        if self.enabled:
            self.current_sample = {}

    def start_timer(self):
        if not self.enabled:
            return None

        return perf_counter()

    def end_timer(self, name, start_time):
        if start_time is None:
            return

        elapsed = (
            perf_counter() - start_time
        ) * 1000

        self.current_sample[name] = (
            self.current_sample.get(name, 0)
            + elapsed
        )

    def finish_sample(self):
        if self.enabled:
            self.history.append(
                self.current_sample.copy()
            )

    def get_averages(self):

        if not self.history:
            return {}

        totals = {}

        for sample in self.history:

            for name, elapsed in sample.items():

                totals[name] = (
                    totals.get(name, 0)
                    + elapsed
                )

        sample_count = len(self.history)

        return {
            name: total / sample_count
            for name, total in totals.items()
        }