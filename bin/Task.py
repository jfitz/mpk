import re
from datetime import (date, timedelta)

from MpkError import (
    MpkTaskError,
    MpkTokenError,
    MpkDurationError,
    MpkParseError
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


class Task:
    def __init__(self, line, known_tids):
        words = line.split()
        # divide into lists for ident, duration
        idents, durations = split_to_lists(words)
        new_idents, old_idents = split_idents(idents, known_tids)

        # validation
        if len(new_idents) != 1:
            raise MpkTaskError('No single new identifier')

        if len(durations) > 1:
            raise MpkTaskError('More than one duration')

        # build task
        self.tid = new_idents[0]
        if len(durations) == 1:
            try:
                self.duration = decode_duration(durations[0])
            except MpkDurationError as error:
                raise MpkTaskError(error.message)
        
        self.predecessors = old_idents


    def set_start(self, start):
        self.start = start
        if self.duration is None:
            self.end = self.start
        else:
            self.end = start + self.duration


    def format_list(self):
        s = self.tid

        if self.duration is not None:
            s += '\t' + str(self.duration.days) + 'd'

        s += '\t' + '[' + ', '.join(self.predecessors) + ']'

        return s


    def format_schedule(self):
        s = self.tid + '\t' + str(self.start) + '\t' + str(self.end)

        return s
