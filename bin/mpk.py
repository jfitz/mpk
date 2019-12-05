#!/usr/bin/python3

import argparse
from datetime import date, datetime
import fileinput
import re

from MpkError import (MpkTaskError, MpkParseError, MpkTokenError)
from Task import Task


def is_date(word):
    return re.match(r'\d\d\d\d-\d\d-\d\d$', word) is not None


def is_ident(word):
    return re.match(r'\w+$', word) is not None


def is_duration(word):
    return re.match(r'\d+[dw]$', word) is not None


def split_to_lists(words):
    idents = []
    durations = []
    dates = []

    for word in words:
        handled = False

        if is_date(word):
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

    return idents, durations, dates


def read_tasks():
  project_first_date = date.today()
  known_tids = []
  tasks = {}
  level_tids = { 0: None }
  levels = [0]
  non_dows = [5, 6]

  for line in fileinput.input([]):
    # remove comments
    if '#' in line:
      line, _ = line.split('#', maxsplit=2)
    line = line.rstrip()

    if len(line) > 0:
      # calculate level
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

      parent_tid = level_tids[level]

      # build a task
      try:
        words = line.split()

        # divide into lists for ident, duration, dates
        idents, durations, dates = split_to_lists(words)

        if len(idents) > 0 or len(durations) > 0:
          task = Task(idents, durations, known_tids, tasks, project_first_date, level, parent_tid, non_dows)
          tid = task.tid
          known_tids.append(tid)
          tasks[tid] = task
          if parent_tid is not None:
            parent_task = tasks[parent_tid]
            parent_task.update(task)
        else:
          if len(dates) == 1:
            project_first_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
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
