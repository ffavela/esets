from eset import Eset
from math import sqrt
VALUE = 2


class Squares(Eset):
    """Something that contains all squares"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = int(sqrt(val))**VALUE - val
        if diff != 0:
            return False
        if self.step > 0 and val >= self.start**VALUE:
            if self.stop is None or\
               val < self.stop**VALUE:
                return True
        if self.step < 0 and self.stop**VALUE < val <= self.start**VALUE:
            return True
        return False

    def index_fun(self, val):
        return (int(sqrt(val)) - self.start) // self.step

    def direct_function(self, i):
        return (self.start + i * self.step) ** VALUE

    def stop_init(self, stop=None):
        return stop


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
