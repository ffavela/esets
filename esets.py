from eset import Eset
from math import sqrt


class Evens(Eset):
    """Something that contains all positive integer evens"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class Multiples(Eset):
    """Something that contains all positive multiples of a number"""
    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.VALUE = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            self.VALUE = args[0]
            super().__init__(xtra_params=(self.VALUE,))
        else:
            self.VALUE = 2
            super().__init__(*args, xtra_params=(self.VALUE,))

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


class Negatives(Eset):
    """Something that contains the Negative Integer numbers"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = self.direct_function(self.start) - val
        if diff % self.step != 0:
            return False
        if self.step > 0 and val <= self.direct_function(self.start):
            if self.stop is None or\
               val > self.direct_function(self.stop):
                return True
        if self.step < 0 and self.direct_function(self.stop) > val \
           >= self.direct_function(self.start):
            return True
        return False

    def inverse_fun(self, val):
        return -(val+1)

    def direct_function(self, i):
        return -(i+1)

    def stop_init(self, stop=None):
        return stop


class Integers(Eset):
    """Something that contains all integers"""
    def __contains__(self, val):
        if not isinstance(val, int):
            return False
        diff = val - self.direct_function(self.start)
        if diff % self.step != 0:
            return False
        if self.step > 0:
            if abs(val) > abs(self.direct_function(self.start)):
                if self.stop is None:
                    return True
                if abs(val) < abs(self.direct_function(self.stop)):
                    return True
                else:  # the abs == case for stop
                    if val < self.direct_function(self.stop):
                        return False
                    else:
                        return True
            if abs(val) == abs(self.direct_function(self.start)):
                if val > self.direct_function(self.start):
                    return False
                else:
                    return True
        if self.step < 0:
            if abs(self.direct_function(self.stop)) <\
               abs(val) < abs(self.direct_function(self.start)):
                return True
            if abs(self.direct_function(self.stop)) == abs(val):
                if val < self.direct_function(self.stop):
                    return True
                else:
                    return False
            if abs(val) == abs(self.direct_function(self.start)):
                if val < self.direct_function(self.start):
                    return False
                else:
                    return True
        return False

    def inverse_fun(self, val):
        if val > 0:
            x = 2*val - 1
        else:
            x = -2*val
        return x

    def direct_function(self, i):
        return (-1)**(i+1) * ((i+1)//2)

    def stop_init(self, stop=None):
        return stop


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


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
