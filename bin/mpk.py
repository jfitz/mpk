#!/usr/bin/python3

import argparse
from datetime import date, datetime
import fileinput
import re

from MpkError import (
  MpkDirectiveError,
  MpkParseError,
  MpkTaskError,
  MpkTokenError
)
from Task import Task


def remove_comments(line):
    # remove comments
    if '#' in line:
      line, _ = line.split('#', maxsplit=1)

    return line.rstrip()


def is_directive(word):
    return re.match(r'\.[A-Za-z0-9-_]*$', word) is not None


def is_date(word):
    return re.match(r'\d\d\d\d-\d\d-\d\d$', word) is not None


def is_ident(word):
    return re.match(r'[A-Za-z][A-Za-z0-9-_]*$', word) is not None


def is_duration(word):
    return re.match(r'\d+d$', word) is not None


def split_to_lists(words, known_dow_keywords, known_ref_keywords):
    directives = []
    dow_keywords = []
    ref_keywords = []
    idents = []
    durations = []
    dates = []

    for word in words:
        handled = False

        if is_directive(word) and not handled:
            directives.append(word)
            handled = True

        if word in known_dow_keywords:
            dow_keywords.append(word)
            handled = True

        if word in known_ref_keywords:
            ref_keywords.append(word)
            handled = True

        if is_date(word) and not handled:
            dates.append(word)
            handled = True

        if is_duration(word) and not handled:
            durations.append(word)
            handled = True

        if is_ident(word) and not handled:
            idents.append(word)
            handled = True
        
        if not handled:
            raise MpkTokenError('Unknown token ' + word)

    return {
        'directives': directives,
        'dow_keywords': dow_keywords,
        'ref_keywords': ref_keywords,
        'identifiers': idents,
        'durations': durations,
        'dates': dates
    }


def calculate_level(line, levels, level_tids, known_tids):
    level = len(line) - len(line.lstrip())
    if level > levels[-1]:
        levels.append(level)
        level_tids[level] = known_tids[-1]
    if level < levels[-1]:
        if level not in level_tids:
            raise MpkParseError('Unexpected indentation',
                                fileinput.filelineno(), line)
        while levels[-1] > level:
            del level_tids[levels[-1]]
            del levels[-1]
    
    return level


def build_task(tokens, known_tids, tasks, project_first_date, level, parent_tid, nonwork_dows):
    idents = tokens['identifiers']
    durations = tokens['durations']
    ref_keywords = tokens['ref_keywords']
    task = Task(idents, durations, known_tids, tasks, project_first_date, level, parent_tid, nonwork_dows, ref_keywords)
    tid = task.tid
    tasks[tid] = task

    if parent_tid is not None:
        parent_task = tasks[parent_tid]
        parent_task.update(task)

    known_tids.append(tid)


def process_directive(tokens, known_dow_keywords, nonwork_dows):
    directives = tokens['directives']
    dow_keywords = tokens['dow_keywords']

    if len(directives) != 1:
      raise MpkDirectiveError('No single directive')

    directive = directives[0]

    handled = False
    
    if directive == '.no-work':
      for keyword in dow_keywords:
        dow = known_dow_keywords[keyword]
        nonwork_dows.append(dow)
      handled = True

    if not handled:
      raise MpkDirectiveError('Unknown directive ' + directive)


def read_tasks():
  project_first_date = date.today()
  known_tids = []
  tasks = {}
  level_tids = { 0: None }
  levels = [0]
  nonwork_dows = []
  known_dow_keywords = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday':4,
    'saturday': 5,
    'sunday': 6
  }
  known_ref_keywords = [ '->' ]

  for line in fileinput.input([]):
    line = remove_comments(line)

    if len(line) > 0:
      level = calculate_level(line, levels, level_tids, known_tids)
      parent_tid = level_tids[level]

      # build a task
      try:
        words = line.split()

        # divide into lists for ident, duration, dates
        tokens = split_to_lists(words, known_dow_keywords, known_ref_keywords)
        directives = tokens['directives']
        dow_keywords = tokens['dow_keywords']
        ref_keywords = tokens['ref_keywords']
        idents = tokens['identifiers']
        durations = tokens['durations']
        dates = tokens['dates']
        

        if len(directives) > 0:
          process_directive(tokens, known_dow_keywords, nonwork_dows)
        else:
          if len(idents) > 0 or len(durations) > 0:
            build_task(tokens, known_tids, tasks, project_first_date, level, parent_tid, nonwork_dows)
          else:
            if len(dates) == 1:
              project_first_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
            else:
              raise MpkParseError('Unknown line', fileinput.filelineno(), line)

      except (MpkTokenError, MpkTaskError) as error:
        raise MpkParseError(
          'Cannot build task: ' + error.message, fileinput.filelineno(), line)

  return known_tids, tasks


def print_list(tids, tasks):
  print('task\tduration\tpredecessors\tresources')

  for tid in tids:
    task = tasks[tid]
    print(task.format_list())


def print_schedule(tids, tasks):
  project_first_date = None
  project_last_date = None

  if len(tasks) > 0:
    tid = tids[0]
    project_first_date = tasks[tid].first_day
    project_last_date = tasks[tid].last_day

  for tid in tids:
    task = tasks[tid]
    if task.first_day < project_first_date:
      project_first_date = task.first_day
    if task.last_day > project_last_date:
      project_last_date = task.last_day

  print('Project first day: ' + str(project_first_date))
  print('Project last day: ' + str(project_last_date))
  print()
  print('task\tstart\tend')

  for tid in tids:
    task = tasks[tid]
    print(task.format_schedule())


parser = argparse.ArgumentParser()
parser.add_argument('--list', help='List items', action='store_true')
parser.add_argument('--schedule', help='Calculate schedule',
                    action='store_true')
args = parser.parse_args()

# read input and parse tasks and durations
try:
  tids, tasks = read_tasks()
except MpkParseError as error:
  print(error.line)
  print('Error: ' + error.message + '  in line: ' + str(error.lineno))
  print('Stopped.')
  quit()

if args.list:
  print_list(tids, tasks)

if args.schedule:
  print_schedule(tids, tasks)
