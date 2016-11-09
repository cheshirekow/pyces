import sys

class FmtWrapper(object):

  def __init__(self, fileobj):
    self.fileobj = fileobj

  def __call__(self, fmt, *args, **kwargs):
    self.fileobj.write(fmt.format(*args, **kwargs))
    return self

  def flush(self):
    self.fileobj.flush()


def fmt_str(fmt, *args, **kwargs):
  return fmt.format(*args, **kwargs)


def fmt_out(fmt, *args, **kwargs):
  return FmtWrapper(sys.stdout)(fmt, *args, **kwargs)


def fmt_err(fmt, *args, **kwargs):
  return FmtWrapper(sys.stderr)(fmt, *args, **kwargs)


def fmt_file(fileobj, fmt, *args, **kwargs):
  return FmtWrapper(fileobj)(fmt, *args, **kwargs)


def fmt_raise(ex_class, fmt, *args, **kwargs):
  raise ex_class(fmt.format(*args, **kwargs))


def fmt_assert(assertion, fmt, *args, **kwargs):
  assert assertion, fmt.format(*args, **kwargs)
