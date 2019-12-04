#!/usr/bin/python3

import argparse
import fileinput
from datetime import date

from MpkError import (MpkTaskError, MpkParseError)
from Task import Task


def read_tasks():
  tasks = []
  for line in fileinput.input([]):
    line = line.rstrip()
    # TODO: remove comment

    if len(line) > 0:
      try:
        task = Task(line)
        tasks.append(task)
      except MpkTaskError as error:
        raise MpkParseError('Cannot build task: ' + error.message, fileinput.filelineno(), line)

  return tasks


def calculate_schedule(tasks):
  project_start_date = date.today()

  for task in tasks:
    task.set_start(project_start_date)


def print_list(tasks):
  print('task\tduration\tprecedents\tresources')

  for task in tasks:
    print(task.format_list())


def print_schedule(tasks):
  print('task\tstart\tend')

  for task in tasks:
    print(task.format_schedule())


parser = argparse.ArgumentParser()
parser.add_argument('--list', help='List items', action='store_true')
parser.add_argument('--schedule', help='Calculate schedule', action='store_true')
args = parser.parse_args()

# read input and parse tasks and durations
try:
  tasks = read_tasks()
except MpkParseError as error:
  print('Error: ' + error.message + '  in line: ' + str(error.lineno) + '  "' + error.line + '"')
  print('Stopped.')
  quit()

if args.list:
  print_list(tasks)

if args.schedule:
  calculate_schedule(tasks)
  print_schedule(tasks)