import threading

PRINT_TRACEBACKS = 0

class ThreadedTaskHandler:
    '''Rather than creating a new thread for each task, reuses existing
    threads for speed.
    '''

    def __init__(self, target_threads=1, limit_threads=0):
        self.queue = []
        self.cond = threading.Condition()
        self.running_threads = 0
        self.idle_threads = 0
        self.target_threads = target_threads
        self.limit_threads = limit_threads

    def addTask(self, task, args=(), kw=None):
        '''
        task is a callable object which will be executed in another
        thread.
        '''

        # if 0:  # Set to 1 to get equivalent but slower processing.  # orig code
        if False:  # Set to True to get equivalent but slower processing.
            if kw is None: kw = {}
            t = threading.Thread(target=task, args=args, kwargs=kw)
            t.setDaemon(1)
            t.start()
            return

        cond = self.cond
        cond.acquire()
        try:
            self.queue.append((task, args, kw))
            if self.idle_threads < 1:
                if self.limit_threads < 1 or (self.running_threads
                                              < self.limit_threads):
                    t = threading.Thread(target=self.clientThread)
                    t.setDaemon(1)
                    self.running_threads = self.running_threads + 1
                    t.start()
            else:
                self.idle_threads = self.idle_threads - 1
            cond.notify()
        finally:
            cond.release()

    def clientThread(self):
        '''
        Performs tasks.
        '''
        exit_loop = 0
        while not exit_loop:
            task = args = kw = None
            cond = self.cond
            cond.acquire()
            try:
                queue = self.queue
                if len(queue) < 1:
                    if self.running_threads > self.target_threads:
                        exit_loop = 1
                        self.running_threads = self.running_threads - 1
                    else:
                        self.idle_threads = self.idle_threads + 1
                        cond.wait()
                if len(queue) > 0:
                    task, args, kw = queue[0]
                    del queue[0]
            finally:
                cond.release()

            if task is not None:
                # ## ZZZDEBUG
                # print ('performing task: %s(%s, %s)\n\r'%(task, args, kw))
                try:
                    if kw is not None:
                        task(*args, **kw)
                    else:
                        task(*args)
                except SystemExit:
                    exit_loop = 1
                    self.running_threads = self.running_threads - 1
                except:
                    if PRINT_TRACEBACKS:
                        # The task ought to do its own error handling,
                        # but sometimes it doesn't.
                        import traceback
                        traceback.print_exc()


if __name__ == '__main__':
    from time import time, sleep
    evt = threading.Event()
    tth = ThreadedTaskHandler()
    start = 0
    end = 0

    class SpeedTest:
        def __init__(self, count):
            self.count = count
        def __call__(self):
            global end
            self.count = self.count - 1
            if self.count <= 0:
                end = time()
                evt.set()
            else:
                tth.addTask(self)

    count = 1000
    t = SpeedTest(count)
    start = time()
    tth.addTask(t)
    evt.wait()
    print('Performed %d tasks in %d ms' % (count,
                                           int((end - start) * 1000)))
