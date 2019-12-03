#!/usr/bin/python3
import fileinput
import re
from MpkError import MpkTokenError

def is_ident(word):
  return re.match('[\w]+$', word) is not None


def is_duration(word):
  return re.match('\d+[dw]$', word) is not None


# read input and parse tasks and durations
tasks = []

try:
  for line in fileinput.input([]):
    line = line.rstrip()
    words = line.split()
    if len(words) > 0:
      task = {}
      for word in words:
        if is_duration(word):
          task['duration'] = word
        else:
          if is_ident(word):
            task['id'] = word
          else:
            raise MpkTokenError(word)
      # validate task has ID
      if 'id' not in task:
        raise MpkTokenError('No ID', fileinput.filelineno(), line)
      tasks.append(task)
except MpkTokenError as error:
  print('Error: ' + error.message + '  in line: ' + str(error.lineno) + '  "' + error.line + '"')
  print('Stopped.')
  quit()
  

# print all tasks
print('task\tduration\tprecedents\tresources')

for task in tasks:
  tid = task['id']
  duration = ''
  if 'duration' in task:
    duration = task['duration']

  print(tid + '\t' + duration)

