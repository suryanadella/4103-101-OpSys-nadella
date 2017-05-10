from queue import Queue
from components.CPU import CPU
from components.Process import Process
from components.Event import Event
from components.Semaphore import Semaphore

class Scheduler:

    def __init__(self, eventMap, events):
        self.eventMap = eventMap
        self.events = events

        # multilevel queue (actually two queues)
        self.q1 = Queue()
        self.q2 = Queue()

        # waiting jobs queue
        self.jobs = Queue()

        # the CPU
        self.cpu = CPU()

        # list of finished processes
        self.finished = []

        # current time
        self.currentTime = 0

        # io queue
        self.io_queue = {}

        # semaphores
        self.semaphore = []
        for i in range(5):
            self.semaphore.append(Semaphore())

    def arrival(self, event):

        # do not process this job
        if event.mem > 512:
            print("This job exceeds the system's main memory capacity.")
            return

        job = Process(event.pid, event.arrival, event.mem, event.time)

        self.jobs.put(job)
        self.job_schedule()

    def job_schedule(self):
        process_added = False
        while True:
            if self.jobs.empty():
                break
            nextjob = self.jobs.get()
            if nextjob.mem <= self.cpu.mem:
                process_added = True
                nextjob.quantum = 100
                nextjob.priority = 1
                nextjob.scheduled_time = self.currentTime
                self.q1.put(nextjob)
                self.cpu.allocate(nextjob.mem)
            else:
                self.jobs.queue.appendleft(nextjob)
                break
        
        self.process_schedule()

    def process_schedule(self):
        if self.cpu.running == None:  # no process running
            nextProcess = None
            if not self.q1.empty():   # get process from q1
                nextProcess = self.q1.get()
            elif not self.q2.empty():
                nextProcess = self.q2.get()
            if nextProcess != None:  # new process in the cpu
                if nextProcess.start_time == None:  # only set start time if it's the first time the process starts
                    nextProcess.start_time = self.currentTime
                self.cpu.running = nextProcess
                complete = self.currentTime + nextProcess.time_left
                expire   = self.currentTime + nextProcess.quantum

                if expire == 9719:
                    expire += 0
                if nextProcess.pid == 40:
                    expire += 0

                nextProcess.last_event = self.currentTime

                pid = nextProcess.pid

                if complete <= expire:
                    newEvent = Event(['T', str(complete)], pid)
                    time = complete
                else:
                    newEvent = Event(['E', str(expire)], pid)
                    time = expire

                nextProcess.pendingEvents.append(newEvent)

                if time not in self.eventMap:
                    self.eventMap[time] = []
                    self.events.put(time)
                self.eventMap[time].append(newEvent)
        else:              # there is a process currently running
            # reschedule if there is a process with higher priority
            if self.cpu.running != None and self.cpu.running.priority == 2 and not self.q1.empty():
                for event in self.cpu.running.pendingEvents:
                    self.deleteEvent(event)
                self.cpu.running.priority = 2
                self.cpu.running.quantum = 300
                self.q2.put(self.cpu.running)
                self.cpu.running = None                              # process out of cpu
                self.process_schedule()

       # running process terminates
    def terminate(self, event):
        ended = self.cpu.running
        ended.complete_time = self.currentTime
        self.cpu.mem += ended.mem
        self.finished.append(ended)
        self.cpu.running = None
        self.job_schedule()

    def deleteEvent(self, e):
        timeEvents = self.eventMap[e.arrival]
        i = 0
        for x in timeEvents:
            if e == x:
                del timeEvents[i]
                break
            i += 1

    # io operation
    def io(self,event):
        io_complete = event.time + self.currentTime
        self.cpu.running.io_start = self.currentTime
        self.cpu.running.io_burst = event.time
        self.cpu.running.io_complete = io_complete
        if io_complete not in self.io_queue:
            self.io_queue[io_complete] = []
        self.io_queue[io_complete].append(self.cpu.running)  # queue current process

        for event in self.cpu.running.pendingEvents:
           # print("delete: %d %s"%(event.arrival, event.kind))
            self.deleteEvent(event)

        self.cpu.running = None                              # process out of cpu
        self.process_schedule()                              # schedule next process
       # pid = self.cpu.running.pid

        io_event = Event(['C', str(io_complete)])
        if io_complete not in self.eventMap:
            self.eventMap[io_complete] = []
            self.events.put(io_complete)
        self.eventMap[io_complete].append(io_event)

    # process quantum expired
    def expired(self, event):
        process = self.cpu.running    # send running process to second queue
        process.quantum = 300
        process.priority = 2
        if process.pid == 40:
            event = event
        self.q2.put(process)
        self.cpu.running = None  # get the process out of the cpu
        self.process_schedule()  # schedule

    # io operation complete
    def io_complete(self, event):   
        complete_list = self.io_queue[self.currentTime]
        for process in complete_list:
            process.quantum = 100
            process.priority = 1
            self.q1.put(process)
        del self.io_queue[self.currentTime]

        self.process_schedule()

    # signal operation
    def signal(self, event):
        signaled = self.semaphore[event.semaphore].signal()
        if signaled != None:
            signaled.quantum = 100
            signaled.priority = 1
            self.q1.put(signaled)
            self.process_schedule()

    # wait operation
    def wait(self, event):
        wait = self.semaphore[event.semaphore].wait(self.cpu.running)
        if wait != None:  # the process needs to wait
            for event in self.cpu.running.pendingEvents:
                self.deleteEvent(event)
            self.cpu.running = None  # take the process out of cpu 
            self.process_schedule()  # and schedule again

    def display(self, event):
        print("")
        print("************************************************************")
        print("")
        print("The status of the simulator at time %d."%self.currentTime)
        print("")
        self.display_job_queue()
        self.display_proc_queue(self.q1, "FIRST", "First")
        self.display_proc_queue(self.q2, "SECOND", "Second")
        self.display_io_queue()
        self.display_semaphore_queue(0, "ZERO")
        self.display_semaphore_queue(1, "ONE")
        self.display_semaphore_queue(2, "TWO")
        self.display_semaphore_queue(3, "THREE")
        self.display_semaphore_queue(4, "FOUR")
        print("The CPU  Start Time  CPU burst time left")
        print("-------  ----------  -------------------")
        print("")
        if self.cpu.running != None:
            print("%7d %11d %20d"%(self.cpu.running.pid, self.cpu.running.start_time, self.cpu.running.time_left))
            print("")
            print("")
        else:
            print("The CPU is idle.\n\n")
        self.display_finished()
        print("There are %d blocks of main memory available in the system.\n"%self.cpu.mem)

    def display_job_queue(self):
        print("The contents of the JOB SCHEDULING QUEUE")
        print("----------------------------------------")
        print("")

        if self.jobs.empty():
            print("The Job Scheduling Queue is empty.")
            print("")
            print("")
        else:
            print("Job #  Arr. Time  Mem. Req.  Run Time")
            print("-----  ---------  ---------  --------")
            print("")
            tmpQueue = Queue()
            while not self.jobs.empty():
                job = self.jobs.get()
                print("%5d %10d %10d %9d"%(job.pid, job.arrival, job.mem, job.runtime))
                tmpQueue.put(job)
            self.jobs = tmpQueue
            print("\n")

    def display_proc_queue(self, q, name, name2):
        header = "The contents of the %s LEVEL READY QUEUE"%name
        header += "\n" + ("-"*(len(header))) + "\n"
        print(header)
        if q.empty():
            print("The %s Level Ready Queue is empty.\n\n"%name2)
        else:
            print("Job #  Arr. Time  Mem. Req.  Run Time")
            print("-----  ---------  ---------  --------")
            print("")
            tmp_q = Queue()
            while not q.empty():
                job = q.get()
                print("%5d %10d %10d %9d"%(job.pid, job.arrival, job.mem, job.runtime))
                tmp_q.put(job)
            if q == self.q1:
                self.q1 = tmp_q
            else:
                self.q2 = tmp_q
            print("\n")


    def display_io_queue(self):
        print("The contents of the I/O WAIT QUEUE")
        print("----------------------------------")
        print("")
        if len(self.io_queue)==0:
            print("The I/O Wait Queue is empty.\n\n")
        else:
            print("Job #  Arr. Time  Mem. Req.  Run Time  IO Start Time  IO Burst  Comp. Time")
            print("-----  ---------  ---------  --------  -------------  --------  ----------")
            print("")
            finished = []
            for time in self.io_queue:
                joblist = self.io_queue[time]
                for job in joblist:
                    finished.append(job)

            finished.sort()

            for job in finished:
                print("%5d %10d %10d %9d %14d %9d %11d"%(job.pid,job.arrival,job.mem,job.runtime,job.io_start,job.io_burst,job.io_complete))
            print("\n")

    def display_semaphore_queue(self, s, name):
        header = "The contents of SEMAPHORE %s"%name
        header += "\n" + ("-"*len(header)) + "\n"
        print(header)
        print("The value of semaphore %d is %d.\n"%(s, self.semaphore[s].value))
        if self.semaphore[s].queue.empty():
            print("The wait queue for semaphore %d is empty.\n\n"%s)
        else:
            tmpQueue = Queue()
            while not self.semaphore[s].queue.empty():
                job = self.semaphore[s].queue.get()
                tmpQueue.put(job)
                print(job.pid)
            print("\n")
            self.semaphore[s].queue = tmpQueue

    def display_finished(self):
        print("The contents of the FINISHED LIST\n---------------------------------")
        print("")
        print("Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time")
        print("-----  ---------  ---------  --------  ----------  ---------")
        print("")

        for job in self.finished:
            print("%5d %10d %10d %9d %11d %10d"%(job.pid,job.arrival,job.mem,job.runtime,job.start_time,job.complete_time))
        print("\n")

    def display_final_stats(self):
        print("")
        print("The contents of the FINAL FINISHED LIST")
        print("---------------------------------------")
        print("")
        print("Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time")
        print("-----  ---------  ---------  --------  ----------  ---------\n")

        average_turnaround = 0
        average_wait_time = 0
        n_finished = len(self.finished)

        for job in self.finished:
            print("%5d %10d %10d %9d %11d %10d"%(job.pid,job.arrival,job.mem,job.runtime,job.start_time,job.complete_time))
            average_turnaround += job.complete_time  - job.arrival
            average_wait_time  += job.scheduled_time - job.arrival
        print("\n")

        average_turnaround /= n_finished
        average_wait_time  /= n_finished
        print("The Average Turnaround Time for the simulation was %.3f units.\n"%average_turnaround)
        print("The Average Job Scheduling Wait Time for the simulation was %.3f units.\n"%average_wait_time)
        print("There are %d blocks of main memory available in the system.\n"%self.cpu.mem)

