from Color import Color
import sys

class ProgressBar:
    """
    Prints percentage completion of a task and updates line as task progresses.
    """
    def __init__(self, task_name=None):
        self.task_name = task_name
        self.update(0.0)
        
    def update(self, ratio):#, task_name=None):
        """Print the current completion progress.
Parameters:
    ratio: float between 0 and 1 indicating the progress"""
        
        if (self.task_name == None):
            message = Color.Yellow + '%.2f%% complete' % (ratio*1e2,) + Color.end
        else:
            message = Color.bold + self.task_name + Color.end + ': ' + Color.Yellow + '%.2f%% complete' % (ratio*1e2,) + Color.end
        sys.stdout.write('\r')
        sys.stdout.write(message)
        sys.stdout.flush()

    def stop(self):#, task_name=None):
        if (self.task_name == None):
            message = Color.green + '%.2f%% complete' % (100,) + Color.end
        else:
            message = Color.bold + self.task_name + Color.end + ': ' + Color.green + '%.2f%% complete' % (100,) + Color.end
        sys.stdout.write('\r')
        sys.stdout.write(message)
        sys.stdout.write('\n')
        sys.stdout.flush()


# Test the progress bar features.
if (__name__ == '__main__'):
    from time import sleep
    def testProgressBar(task_name=None):
        if (task_name == None):
            print "Print some text before starting an unnamed process."
        else:
            print "Print some text before starting process named: '"+task_name+"'"
        pp = progressBar(task_name=task_name)
        tot = 4
        for ii in range(tot):
            sleep(0.8)
            pp.update(float(ii+1)/float(tot))
        pp.stop()
        print "Print some text after finishing process."
        sleep(0.8)

    testProgressBar()
    print
    testProgressBar('Fun task')
