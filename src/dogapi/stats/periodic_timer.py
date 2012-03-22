"""
A small class to run a task periodically in a thread.
"""


from threading import Thread, Event


class PeriodicTimer(Thread):
    def __init__(self, interval, function, *args, **kwargs):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def end(self):
        self.finished.set()

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.isSet():
                break
            self.function(*self.args, **self.kwargs)
