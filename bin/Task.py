class Task:
    def __init__(self, tid):
        self.tid = tid


    def set_duration(self, duration):
        self.duration = duration


    def set_start(self, start):
        self.start = start
        self.end = start + self.duration


    def format_list(self):
        return self.tid + '\t' + str(self.duration.days) + 'd'


    def format_schedule(self):
        return self.tid + '\t' + str(self.start) + '\t' + str(self.end)
