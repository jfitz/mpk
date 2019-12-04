#!/usr/bin/python3
import argparse
import fileinput
import re
from datetime import (date, timedelta)
from MpkError import (MpkTokenError, MpkDecodeError)
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


def read_tasks():
  tasks = []
  for line in fileinput.input([]):
    line = line.rstrip()
    words = line.split()
    if len(words) > 0:
      task = Task()
      for word in words:
        if is_duration(word):
          task.set_duration(decode_duration(word))
        else:
          if is_ident(word):
            task.set_tid(word)
          else:
            raise MpkTokenError(word, fileinput.filelineno(), line)
      # validate task has ID
      tasks.append(task)
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
except MpkTokenError as error:
  print('Error: ' + error.message + '  in line: ' + str(error.lineno) + '  "' + error.line + '"')
  print('Stopped.')
  quit()

if args.list:
  print_list(tasks)

if args.schedule:
  calculate_schedule(tasks)
  print_schedule(tasks)