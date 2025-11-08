from eset import Eset


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


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
