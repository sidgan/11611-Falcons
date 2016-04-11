import re
import time
import warnings
from spacy.en import English

__author__ = 'pbamotra'

nlp = English()
WORD = re.compile(r'\w+')
# ------------ Controls if the system runs in simulation mode or production mode ------------ #
IS_PRODUCTION_MODE = True
# ------------------------------------------------------------------------------------------- #
CANDIDATE_THRESHOLD = 10
USE_PICKLE = True


def deprecated(func):
    """
    This is a decorator which can be used to mark functions as deprecated.

    :param func: function to be marked as deprecated
    """

    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te - ts)
        return result

    return timed
