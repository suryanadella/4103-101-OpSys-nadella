from queue import Queue

class Semaphore:

    def __init__(self):
        self.value = 1
        self.queue = Queue()

    def wait(self, process):
        self.value -= 1
        if self.value < 0:
            self.queue.put(process)  # the process needs to wait, so we queue it
            return process
        return None            

    def signal(self):
        self.value += 1
        signaled = None
        if not self.queue.empty():
            return self.queue.get()