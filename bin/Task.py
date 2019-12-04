import re
from datetime import (date, timedelta)

from MpkError import (
    MpkDurationError,
    MpkParseError,
    MpkScheduleError,
    MpkTaskError,
    MpkTokenError
)

def is_ident(word):
    return re.match(r'[\w]+$', word) is not None


def is_duration(word):
    return re.match(r'\d+[dw]$', word) is not None


def split_to_lists(words):
    idents = []
    durations = []

    for word in words:
        handled = False

        if is_duration(word):
            durations.append(word)
            handled = True

        if is_ident(word) and not handled:
            idents.append(word)
            handled = True
        
        if not handled:
            raise MpkTokenError('Unknown token ' + word)

    return idents, durations


def split_idents(idents, known_idents):
    new_idents = []
    old_idents = []

    for ident in idents:
        if ident in known_idents:
            old_idents.append(ident)
        else:
            new_idents.append(ident)
    
    return new_idents, old_idents


def decode_duration(word):
    if len(word) == 0:
        raise MpkDurationError('Empty duration')

    duration = timedelta(days = 0)

    if word[-1] == 'd':
        daycount = int(word[:-1])
        duration = timedelta(days = daycount)

    return duration


def is_nonworkday(d):
    dow = d.weekday()
    return dow >= 5


class Task:
    def __init__(self, line, known_tids, tasks, project_start_date):
        words = line.split()
        # divide into lists for ident, duration
        idents, durations = split_to_lists(words)
        new_idents, old_idents = split_idents(idents, known_tids)

        # validation
        if len(new_idents) != 1:
            raise MpkTaskError('No single new identifier')

        if len(durations) > 1:
            raise MpkTaskError('More than one duration')

        # assign values
        self.tid = new_idents[0]
        self.predecessors = old_idents

        # must start no earlier than project start date
        possible_start = project_start_date
        # must start no earlier than predecessor end date + 1
        one_day = timedelta(days = 1)
        for tid in self.predecessors:
            task = tasks[tid]
            task_possible_start = task.end + one_day
            if task_possible_start > possible_start:
                possible_start = task_possible_start

        self.start = possible_start

        # decode task duration and compute end date and work days
        self.work_days = []
        self.end = self.start
        if len(durations) == 1:
            try:
                self.duration = decode_duration(durations[0])
                self.end = self.start
                day_count = self.duration.days
                for i in range(0, day_count):
                    self.work_days.append(self.end)
                    self.end = self.end + one_day
                    # while this new day is a non-workday
                    # move to the next day (stop after 14)
                    limit = 14
                    count = 0
                    while is_nonworkday(self.end):
                        self.end = self.end + one_day
                        count += 1
                        if count > limit:
                            raise MpkScheduleError('More than ' + str(limit) + ' non-workdays')
            except MpkDurationError as error:
                raise MpkTaskError(error.message)
        

    def format_list(self):
        s = self.tid

        if self.duration is not None:
            s += '\t' + str(self.duration.days) + 'd'

        s += '\t' + '[' + ', '.join(self.predecessors) + ']'

        if len(self.work_days) > 0:
            strings = []
            for work_day in self.work_days:
                strings.append(str(work_day))
            s += '\t' + '[' + ', '.join(strings) + ']'

        return s


    def format_schedule(self):
        s = self.tid + '\t' + str(self.start) + '\t' + str(self.end)

        return s
