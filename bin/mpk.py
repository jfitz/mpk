#!/usr/bin/python3
import argparse
import fileinput
import re
from datetime import (date, timedelta)
from MpkError import (MpkTokenError, MpkDecodeError)


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
      task = {}
      for word in words:
        if is_duration(word):
          duration = decode_duration(word)
          task['duration'] = duration
        else:
          if is_ident(word):
            task['id'] = word
          else:
            raise MpkTokenError(word, fileinput.filelineno(), line)
      # validate task has ID
      if 'id' not in task:
        raise MpkTokenError('No ID', fileinput.filelineno(), line)
      tasks.append(task)
  return tasks


def calculate_schedule(tasks):
  project_start_date = date.today()

  for task in tasks:
    if 'duration' in task:
      duration = task['duration']
      task['start'] = project_start_date
      task['end'] = project_start_date + duration


def format_task_list(task):
    tid = task['id']
    duration = ''
    if 'duration' in task:
      duration = task['duration']

    return tid + '\t' + str(duration.days) + 'd'


def print_list(tasks):
  print('task\tduration\tprecedents\tresources')

  for task in tasks:
    print(format_task_list(task))


def format_task_schedule(task):
    tid = task['id']
    start = ''
    end = ''
    if 'start' in task:
      start = task['start']
    if 'end' in task:
      end = task['end']

    return tid + '\t' + str(start) + '\t' + str(end)


def print_schedule(tasks):
  print('task\tstart\tend')

  for task in tasks:
    print(format_task_schedule(task))

parser = argparse.ArgumentParser()
parser.add_argument('--schedule', help='Calculate schedule', action='store_true')
args = parser.parse_args()

# read input and parse tasks and durations
try:
  tasks = read_tasks()
except MpkTokenError as error:
  print('Error: ' + error.message + '  in line: ' + str(error.lineno) + '  "' + error.line + '"')
  print('Stopped.')
  quit()

if not args.schedule:
  print_list(tasks)

if args.schedule:
  calculate_schedule(tasks)
  print_schedule(tasks)