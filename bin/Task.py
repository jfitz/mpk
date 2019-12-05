from datetime import (date, timedelta)

from MpkError import (
    MpkDurationError,
    MpkParseError,
    MpkScheduleError,
    MpkTaskError,
    MpkTokenError
)

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


def calc_work_days(first_day, duration):
    day_count = duration.days
    one_day = timedelta(days = 1)
    last_day = first_day
    walk = first_day
    work_days = []
    for _ in range(0, day_count):
        work_days.append(walk)
        walk = walk + one_day
        # while this new day is a non-workday
        # move to the next day (stop after 14)
        limit = 14
        count = 0
        while is_nonworkday(walk):
            walk = walk + one_day
            count += 1
            if count > limit:
                raise MpkScheduleError(
                    'More than ' + str(limit) + ' non-workdays')
    
    if len(work_days) > 0:
        last_day = work_days[-1]

    return last_day, work_days


class Task:
    def __init__(self, idents, durations, known_tids, tasks, project_first_day_date, level, parent_tid):
        new_idents, old_idents = split_idents(idents, known_tids)

        # validation
        if len(new_idents) != 1:
            raise MpkTaskError('No single new identifier')

        if len(durations) > 1:
            raise MpkTaskError('More than one duration')

        # assign values
        self.tid = new_idents[0]
        self.predecessors = old_idents
        if parent_tid is not None:
            self.predecessors.append(parent_tid)
        self.duration = None
        self.level = level

        # must start no earlier than project start date
        possible_first_day = project_first_day_date
        # must start no earlier than predecessor end date + 1
        one_day = timedelta(days = 1)
        for tid in self.predecessors:
            task = tasks[tid]
            task_possible_first_day = task.last_day + one_day
            if task_possible_first_day > possible_first_day:
                possible_first_day = task_possible_first_day

        self.first_day = possible_first_day

        # decode task duration and compute last day and work days
        self.work_days = []
        self.last_day = self.first_day - one_day
        if len(durations) == 1:
            try:
                self.duration = decode_duration(durations[0])
                self.last_day, self.work_days = calc_work_days(self.first_day, self.duration)

            except (MpkDurationError, MpkScheduleError) as error:
                raise MpkTaskError(error.message)


    def update(self, child_task):
        if child_task.last_day > self.last_day:
            self.last_day = child_task.last_day


    def format_list(self):
        s = self.tid

        s += ' (' + str(self.level) + ')'

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
        s = self.tid + '\t' + str(self.first_day) + '\t' + str(self.last_day)

        return s
