import multiprocessing
import threading
import time
import sys

from math import fabs

try:
    TIME_FUNC = time.perf_counter
except AttributeError:
    TIME_FUNC = time.monotonic

# Default precision
DEF_PRECISION = 4
# Default time step
DEF_STEP = 0.01


def write_time(start_time, precision, step):
    cur_time = '{0:.{1}f}'.format(fabs(TIME_FUNC() - start_time), precision)
    sys.stdout.write(cur_time)
    sys.stdout.flush()
    time.sleep(step)
    sys.stdout.write('\b' * len(cur_time))


class InlineTimer(object):
    def __init__(self, name=None, precision=DEF_PRECISION, step=DEF_STEP):
        self.stop_event = None
        self.par_type = None
        self.par = None
        self.precision = precision
        self.step = step
        self.name = name or type(self).__name__
        self.start_time = TIME_FUNC()

    def start(self):
        self.stop_event.clear()
        self.par = self.par_type(
            name=self.name, target=self.init_time, daemon=True)
        self.par.start()

    def stop(self):
        if self.par is not None:
            self.stop_event.set()
            self.par.join()

    def init_time(self):
        while not self.stop_event.is_set():
            write_time(self.start_time, self.precision, self.step)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


class ProcessTimer(InlineTimer):
    def __init__(self, name=None, precision=DEF_PRECISION, step=DEF_STEP):
        super().__init__(name, precision, step)
        self.par_type = multiprocessing.Process
        self.stop_event = multiprocessing.Event()


class ThreadTimer(InlineTimer):
    def __init__(self, name=None, precision=DEF_PRECISION, step=DEF_STEP):
        super().__init__(name, precision, step)
        self.par_type = threading.Thread
        self.stop_event = threading.Event()


def process_timer(name=None, prec=DEF_PRECISION, step=DEF_STEP):
    return ProcessTimer(name, prec, step)


def thread_timer(name=None, prec=DEF_PRECISION, step=DEF_STEP):
    return ThreadTimer(name, prec, step)


def inline_timer(mp=False, **kwargs):
    if mp:
        return process_timer(**kwargs)
    else:
        return thread_timer(**kwargs)
