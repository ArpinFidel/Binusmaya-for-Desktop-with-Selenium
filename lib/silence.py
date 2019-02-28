import contextlib
import sys

class DummyFile(object):
    def write(self, x): pass
    def flush(self): pass

@contextlib.contextmanager
def no_stdout():
    sys.stdout = DummyFile()
    try:
    	yield
    except:
    	raise
    finally:
    	sys.stdout = sys.__stdout__
