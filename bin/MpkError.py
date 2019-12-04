class MpkError(Exception):
  pass


class MpkTokenError(MpkError):
  def __init__(self, message):
    self.message = message


class MpkParseError(MpkError):
  def __init__(self, message, lineno, line):
    self.message = message
    self.lineno = lineno
    self.line = line


class MpkDecodeError(MpkError):
  def __init__(self, message):
    self.message = message
