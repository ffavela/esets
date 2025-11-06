from eset import Eset
from math import sqrt
VALUE = 2


class Squares(Eset):
    """Something that contains all squares"""
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
        return int(sqrt(val))

    def direct_function(self, i):
        return i ** VALUE

    def stop_init(self, stop=None):
        return stop


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
