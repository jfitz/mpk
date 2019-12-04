class Task:
    def __init__(self, tid, duration = None):
        self.tid = tid
        self.duration = duration


    def set_start(self, start):
        self.start = start
        if self.duration is None:
            self.end = self.start
        else:
            self.end = start + self.duration


    def format_list(self):
        if self.duration is None:
            s = self.tid
        else:
            s = self.tid + '\t' + str(self.duration.days) + 'd'

        return s


    def format_schedule(self):
        s = self.tid + '\t' + str(self.start) + '\t' + str(self.end)

        return s
