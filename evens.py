from eset import Eset
VALUE = 2


class Evens(Eset):
    """Something that contains all positive integer evens"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = val - self.start * VALUE
        if diff % (VALUE*self.step) != 0:
            return False
        if self.step > 0 and val >= self.start*VALUE:
            if self.stop is None or\
               val < self.stop*VALUE:
                return True
        if self.step < 0 and self.stop*VALUE < val <= self.start*VALUE:
            return True
        return False

    def index_fun(self, val):
        return (val - self.start * VALUE)//(VALUE * self.step)

    def direct_function(self, i):
        return (self.start + i * self.step) * VALUE


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
