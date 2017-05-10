class Event:

    def __init__(self, parts, pid = None):
        self.arrival = int(parts[1].strip())
        self.kind = parts[0].strip()

        #self.pid = pid

        if self.kind == "A":
            self.pid  = int(parts[2].strip())
            self.mem  = int(parts[3].strip())
            self.time = int(parts[4].strip())
        elif self.kind == "I":
            self.time = int(parts[2].strip())
        elif self.kind == "S" or self.kind == "W":
            self.semaphore = int(parts[2].strip())
            
    def __lt__(self, other):
        if self.arrival < other.arrival:
            return True

        if self.arrival > other.arrival:
            return False

        # same arrival

        if self.kind == other.kind:
            1/0

        # internal events should be treated first
        if self.kind in ["C","E","T"] and other.kind in ["D", "S", "I", "A"]:
            return True

        if other.kind in ["C","E","T"] and self.kind in ["D", "S", "I", "A"]:
            return False

        # both are intenal events
        1/0



