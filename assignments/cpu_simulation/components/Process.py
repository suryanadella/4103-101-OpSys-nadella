class Process:

    def __init__(self, pid, arrival, mem, runtime):
        self.pid = pid
        self.arrival = arrival
        self.mem     = mem
        self.runtime = runtime
        self.quantum = None
        self.complete_time = None
        self.start_time = None
        self.time_left = self.runtime
        self.last_event = None
        self.pendingEvents = []  # list of pending events for this process
        self.io_start = None
        self.io_burst = None
        self.io_complete = None
        self.priority = None
        self.scheduled_time = None

    def __lt__(self, other):
        return self.io_complete < other.io_complete
