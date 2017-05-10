class CPU:

    def __init__(self):
        self.running = None
        self.mem     = 512

    def allocate(self, mem):
        self.mem -= mem

    def deallocate(self, mem):
        self.mem += mem


