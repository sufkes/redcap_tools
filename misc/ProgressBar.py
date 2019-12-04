from Color import Color
import sys

class ProgressBar:
    """
    Prints percentage completion of a task and updates line as task progresses.
    """
    def __init__(self, task_name=None):
        self.task_name = task_name
        self.update(0.0)

#    def makeMessage(self, ratio, task_name):
#        if (task_name == None):
#            message = '%.2f%% complete' % (ratio*1e2,)
#        else:
#            message = task_name+': %.2f%% complete' % (ratio*1e2,)
#        return message

    def update(self, ratio):#, task_name=None):
        if (self.task_name == None):
            message = Color.Yellow + '%.2f%% complete' % (ratio*1e2,) + Color.end
        else:
            message = Color.bold + self.task_name + Color.end + ': ' + Color.Yellow + '%.2f%% complete' % (ratio*1e2,) + Color.end
#        message = Color.Yellow + self.makeMessage(ratio, self.task_name) + Color.end
        sys.stdout.write('\r')
        sys.stdout.write(message)
        sys.stdout.flush()

    def stop(self):#, task_name=None):
        if (self.task_name == None):
            message = Color.green + '%.2f%% complete' % (100,) + Color.end
        else:
            message = Color.bold + self.task_name + Color.end + ': ' + Color.green + '%.2f%% complete' % (100,) + Color.end
#        message = Color.green + self.makeMessage(1.0, self.task_name) + Color.end
        sys.stdout.write('\r')
#        sys.stdout.write('%.2f%% complete' % (float(100),))
        sys.stdout.write(message)
        sys.stdout.write('\n')
        sys.stdout.flush()


#    def start(self):
#        self.s = time()
#        print Color.blue+self.description+": "+Color.green+"Start"+Color.end

#    def stop(self):
#        self.e = time()
#        print Color.blue+self.description+": "+Color.red+"Stop"+Color.end
#        self.report()

#    def report(self):
#        print Color.blue+'Time taken: '+Color.end+"{:.2f}".format(self.e - self.s)+'s'

# Run a test if called directly.
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
