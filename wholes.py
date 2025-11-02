from eset import Eset


class Wholes(Eset):
    """Something that contains the Whole numbers"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = val - self.start
        if diff % self.step != 0:
            return False
        if self.step > 0 and val >= self.start:
            if self.stop is None or\
               val < self.stop:
                return True
        if self.step < 0 and self.stop < val <= self.start:
            return True
        return False

    def index_fun(self, val):
        return (val - self.start)//(self.step)

    def direct_function(self, i):
        return self.start + i * self.step

    def stop_init(self, stop=None):
        return stop


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
