from eset import Eset


class Wholes(Eset):
    """Something that contains the Whole numbers"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = self.direct_function(self.start) - val
        if diff % self.step != 0:
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
        return val

    def direct_function(self, i):
        return i

    def stop_init(self, stop=None):
        return stop
