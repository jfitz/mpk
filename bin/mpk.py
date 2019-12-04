#!/usr/bin/python3

import argparse
import fileinput
from datetime import date

from MpkError import (MpkTaskError, MpkParseError)
from Task import Task


def read_tasks():
  known_tids = []
  tasks = {}

  for line in fileinput.input([]):
    line = line.rstrip()
    # TODO: remove comment

    if len(line) > 0:
      try:
        task = Task(line, known_tids)
        tid = task.tid
        known_tids.append(tid)
        tasks[tid] = task
      except MpkTaskError as error:
        raise MpkParseError('Cannot build task: ' + error.message, fileinput.filelineno(), line)

  return known_tids, tasks


def calculate_schedule(tids, tasks):
  project_start_date = date.today()

  for tid in tids:
    task = tasks[tid]
    task.set_start(project_start_date)


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
parser.add_argument('--schedule', help='Calculate schedule', action='store_true')
args = parser.parse_args()

# read input and parse tasks and durations
try:
  tids, tasks = read_tasks()
except MpkParseError as error:
  print('Error: ' + error.message + '  in line: ' + str(error.lineno) + '  "' + error.line + '"')
  print('Stopped.')
  quit()

if args.list:
  print_list(tids, tasks)

if args.schedule:
  calculate_schedule(tids, tasks)
  print_schedule(tids, tasks)
  