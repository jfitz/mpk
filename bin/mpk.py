#!/usr/bin/python3

import argparse
import fileinput
from datetime import date

from MpkError import (MpkTaskError, MpkParseError)
from Task import Task


def read_tasks():
  project_first_date = date.today()
  known_tids = []
  tasks = {}
  level_tids = { 0: None }
  levels = [0]

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
        task = Task(line, known_tids, tasks, project_first_date, level, parent_tid)
        tid = task.tid
        known_tids.append(tid)
        tasks[tid] = task
        if parent_tid is not None:
          parent_task = tasks[parent_tid]
          parent_task.update(task)
      except MpkTaskError as error:
        raise MpkParseError(
          'Cannot build task: ' + error.message, fileinput.filelineno(), line)

  return known_tids, tasks


def print_list(tids, tasks):
  print('task\tduration\tpredecessors\tresources')

  for tid in tids:
    task = tasks[tid]
    print(task.format_list())


def print_schedule(tids, tasks):
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
