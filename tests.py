import time

from inline_timer import thread_timer


if __name__ == '__main__':
    tmr = thread_timer()
    with thread_timer():
        time.sleep(5)
