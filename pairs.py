import pdb

VALUE = 2


class Pairs:
    """Something that contains all positive integer pairs"""
    def __init__(self, start=0, stop=None, step=1,
                 raw_repr=False):
        if start is None:
            start = 0
        if not isinstance(step, int):
            raise ValueError('Values need to be integers.')
        if stop is not None:
            if not isinstance(stop, int):
                raise ValueError('Values need to be integers.')
        if start < 0 and stop is None:
            raise ValueError('No last value exists.')

        self.start = start
        self.step = step
        self.stop = stop
        self.raw_repr = raw_repr

    def step_function(self, i: int) -> int:
        """A simple step function"""
        if i == 0:
            return 0
        return 1

    def __len__(self):
        if self.stop is not None:
            delta = abs(self.stop - self.start)
            return self.step_function(delta % self.step) +\
                delta // abs(self.step)
        raise ValueError('Aleph_0 infinite')

    def __getitem__(self, key):
        if isinstance(key, slice):
            kstep = key.step
            if key.step is None:
                step = self.step
                kstep = 1
            else:
                step = self.step * key.step

            flip = True if step * self.step < 0 else False

            if key.start is None:
                s_start = self.start
            else:  # Assuming happy path with no negative vals
                s_start = self.start + key.start * self.step

            if key.stop is None:
                s_stop = self.stop
            else:
                s_stop = self.start + key.stop * self.step

            if s_stop < s_start and self.step > 0 \
               or s_stop > s_start and self.step < 0:
                delta = 0
            else:
                delta = abs(s_stop - s_start)

            len_raw = delta // abs(self.step) +\
                self.step_function(delta % self.step)
            len_step = len_raw // abs(kstep) +\
                self.step_function(delta % kstep)

            start = s_start
            stop = start + len_step * abs(step)

            if flip:
                if self.step > 0:  # step < 0
                    new_start = stop + step
                    new_stop = new_start + len_step * step
                if self.step < 0:  # step > 0
                    new_start = s_stop + step
                    new_stop = s_start + step
                start, stop = new_start, new_stop

            return Pairs(start, stop, step, self.raw_repr)

        if isinstance(key, int):
            i = int(key)
            if i < 0:
                if self.stop is None:
                    msg = 'Cannot count backward from an Aleph_0 infinite set'
                    raise IndexError(msg)
                if i + self.__len__() < 0:
                    raise IndexError('eset index out of range')
                i = self.__len__() + i
            if i >= 0:
                if self.stop is None or i < self.__len__():
                    return (self.start + i * self.step) * VALUE
                raise IndexError('eset index out of range')
        raise ValueError('Need a slice or a positive integer')

    def __contains__(self, val):
        if val % (VALUE*self.step) != 0:
            return False
        if val >= self.start*VALUE:
            if self.stop is None or\
               val < (self.start+self.__len__()*self.step)*VALUE:
                return True
        # Need to set the step < 0 case
        return False

    def index(self, val):
        if val not in self:
            cls = type(self)
            msg = f'{val!r} not in {cls.__name__!r}'
            raise ValueError(msg)
        return (val - self.start * VALUE)//(VALUE * self.step)

    # There are better ways, but this is good enough
    def __iter__(self, i=0):
        if self.stop is None:
            while True:
                yield VALUE * (self.start + i * self.step)
                i += 1
        else:
            while i < self.__len__():
                yield VALUE * (self.start + i * self.step)
                i += 1

    def __repr__(self):
        return get_repr_str(self)


def get_repr_str(obj: Pairs, max_val: int = 4) -> str:
    if not obj.raw_repr:
        ellipsis = ', ...'
        try:
            last = min(max_val, len(obj))
            if max_val >= len(obj):
                ellipsis = ''
        except ValueError:
            last = max_val
        rstr = ', '.join([str(v) for v in obj[:last]])
        rstr += ellipsis
        return f'<esets.Pairs ({rstr})>'
    else:
        return f'obj.start = {obj.start},\n' +\
            f'obj.stop = {obj.stop},\n' +\
            f'obj.step = {obj.step}'


if __name__ == '__main__':
    import doctest
    # doctest.testfile("pairsDocTest.txt")
    doctest.testfile("pairsDocTestSmall.txt")
