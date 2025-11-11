from eset import Eset
from math import sqrt


class Squares(Eset):
    """Something that contains all squares"""
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.VALUE = 2

    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = self.direct_function(self.inverse_fun(val)) - val
        if diff != 0:
            return False
        if self.step > 0 and val >= self.direct_function(self.start):
            if self.stop is None or\
               val < self.direct_function(self.stop):
                return True
        if self.step < 0 and self.direct_function(self.stop) < val \
           <= self.direct_function(self.start):
            return True
        return False

    def inverse_fun(self, val):
        # Not perfect because it is going through the floats, is there
        # a better way?
        return int(sqrt(val))

    def direct_function(self, i):
        return i ** self.VALUE

    def stop_init(self, stop=None):
        return stop
