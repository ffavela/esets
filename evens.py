from eset import Eset


class Evens(Eset):
    """Something that contains all positive integer evens"""
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.VALUE = 2

    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = val - self.direct_function(self.start)
        if diff % self.direct_function(self.step) != 0:
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
        return val // self.VALUE

    def direct_function(self, i):
        return i * self.VALUE

    def stop_init(self, stop=None):
        return stop


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
