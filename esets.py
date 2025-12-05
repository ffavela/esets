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


class Float64_tpls(Eset):
    """Something that contains all the float 64 using the IEEE 754
    double precision format as tuples

    """
    def __contains__(self, val):
        if not isinstance(val, tuple):
            return False
        s_bit, exponent, significand = val
        if not isinstance(s_bit, int) or\
           not isinstance(exponent, int) or\
           not isinstance(significand, int):
            return False
        if s_bit not in (0, 1):
            return False
        if not 0 <= exponent < 2**11:
            return False
        if not 0 <= significand < 2**52:
            return False
        return True

    def inverse_fun(self, val):
        s_bit, exponent, significand = val
        if s_bit:
            return self.neg_offset - (exponent * 2**53 + significand)
        else:
            return exponent * 2**53 + significand

    def get_e_s(self, i):
        e, s = 0, i
        for j in range(64, 52, -1):
            e += (s // 2**j) * 2**(j-53)
            s %= 2**j
        return e, s

    def direct_function(self, i):
        if (-1)**(i+1) < 0:
            s_bit = 0
        else:
            s_bit = 1
        v = (i+1)//2
        exponent, significand = self.get_e_s(v)
        return (s_bit, exponent, significand)

    def stop_init(self, stop=None):
        return 2**65-1  # == 1 + 2^1 + 2^2 + ... + 2^64


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
