#!/usr/bin/python3

import argparse
import fileinput
import re
from datetime import (date, timedelta)

from MpkError import (
  MpkTokenError,
   MpkDecodeError,
   MpkParseError
   )
from Task import Task


def is_ident(word):
  return re.match(r'[\w]+$', word) is not None


def is_duration(word):
  return re.match(r'\d+[dw]$', word) is not None


def decode_duration(word):
  if len(word) == 0:
    raise MpkDecodeError('Empty duration')

  duration = timedelta(days = 0)

  if word[-1] == 'd':
    daycount = int(word[:-1])
    duration = timedelta(days = daycount)

  return duration


def split_to_lists(words, line):
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


def read_tasks():
  tasks = []
  for line in fileinput.input([]):
    line = line.rstrip()
    words = line.split()

    if len(words) > 0:
      try:
        # divide into lists for ident, duration
        idents, durations = split_to_lists(words, line)

        # validation
        if len(idents) != 1:
          raise MpkParseError('No single new identifier', fileinput.filelineno(), line)

        if len(durations) > 1:
          raise MpkParseError('More than one duration', fileinput.filelineno(), line)

        # build task
        task = Task(idents[0])
        if len(durations) == 1:
          task.set_duration(decode_duration(durations[0]))

        tasks.append(task)

      except MpkTokenError as error:
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