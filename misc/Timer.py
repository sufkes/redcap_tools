from Color import Color
from time import time

class Timer:
    """
    Tool for timing segment of code. Prints message to indicate that code segment
    is being executed on instantiation. Prints message to indicate that code segment
    is complete, along with the time taken, when the stop() method is called.

    Usage:
    t = Timer('description of segment of code')
    # segment of code you wish to time
    # .
    # .
    # .
    t.stop()

    Notes
    - The timer can be restarted using the start() method.
    - The stop() method can be called multiple times. Each time, the time since the 
    last execution of start() will be reported.
    """
    def __init__(self, description):
        self.description = description
        self.start()

    def start(self):
        self.s = time()
        print Color.blue+self.description+": "+Color.green+"Start"+Color.end

    def stop(self):
        self.e = time()
        print Color.blue+self.description+": "+Color.red+"Stop"+Color.end
        self.report()

    def report(self):
        print Color.blue+'Time taken: '+Color.end+"{:.2f}".format(self.e - self.s)+'s'

    

