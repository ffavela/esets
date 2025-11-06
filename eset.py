import abc
import sys


class Eset(abc.ABC):
    def __init__(self, start=0, stop=None, step=1,
                 raw_repr=False, sliced=False):
        if not sliced:
            stop = self.stop_init()
        if start is None:
            start = 0
        if not isinstance(step, int):
            raise ValueError('Values need to be integers.')
        if stop is not None:
            if not isinstance(stop, int):
                raise ValueError('Values need to be integers.')
        if start < 0 and stop is None:
            raise ValueError('No last value exists.')
        if stop is not None:
            if stop < start and step > 0 \
               or stop > start and step < 0:
                raise ValueError('Invalid initialization state.')
        self.start = start
        self.step = step
        self.stop = stop
        self.sliced = sliced
        self.raw_repr = raw_repr

    def step_function(self, i: int) -> int:
        """A simple step function"""
        if i == 0:
            return 0
        return 1

    def __len__(self):
        ret_len = self.len()
        if ret_len <= sys.maxsize:
            return ret_len
        raise NotImplementedError('__len__ is limited use obj.len() instead')

    def len(self):
        if self.stop is not None:
            delta = abs(self.stop - self.start)
            return self.step_function(delta % self.step) +\
                delta // abs(self.step)
        raise ValueError('Aleph_0 infinite')

    def __getitem__(self, key):
        enum_error = 'Cannot enumerate backward from infinite'
        if isinstance(key, slice):
            kstep = key.step
            if key.step is None:
                step = self.step
                kstep = 1
            else:
                step = self.step * key.step

            flip = True if step * self.step < 0 else False

            if key.stop is None:
                s_stop = self.stop
            else:
                kstop = key.stop
                if kstop < 0:
                    if self.stop is None:
                        raise ValueError(enum_error)
                    if self.len() < -kstop:  # cause kstop < 0
                        kstop = -1
                    else:
                        # The following satisfies:
                        # 0 < kstop < self.len()
                        kstop += self.len()
                # The next satisfies kstop > 0 too
                elif flip and kstop >= self.len():
                    kstop = self.len() - 1
                s_stop = self.start + kstop * self.step

            if s_stop is None and step < 0:
                raise ValueError(enum_error)

            if key.start is None:
                s_start = self.start
            else:
                kstart = key.start
                if kstart < 0:
                    if s_stop is None:
                        raise ValueError(enum_error)
                    if self.len() < -kstart:  # cause kstart < 0
                        kstart = -1
                    else:
                        # The following satisfies:
                        # 0 < kstart < self.len()
                        kstart += self.len()
                # The next satisfies kstart > 0 too
                elif flip and kstart > self.len():
                    kstart = self.len() - 1
                # If despite of trying it is still negative
                if not flip and kstart < 0:
                    kstart = 0
                s_start = self.start + kstart * self.step

            if flip and step < 0:
                if key.stop is None:
                    s_stop = self.start - self.step
                if key.start is None:
                    if self.stop is None:
                        s_start = s_stop - self.step
                    else:
                        s_start = self.stop - self.step

            if s_stop is None:
                start = s_start
                stop = s_stop
            else:
                if (s_stop < s_start and step > 0
                   or s_stop > s_start and step < 0)\
                   and (key.start is not None or
                        key.stop is not None):
                    delta = 0
                else:
                    delta = abs(s_stop - s_start)

                len_raw = delta // abs(self.step) +\
                    self.step_function(delta % self.step)
                len_step = len_raw // abs(kstep) +\
                    self.step_function(len_raw % kstep)

                start = s_start
                stop = start + len_step * step

            if flip:
                if self.step < 0:  # step > 0
                    start, stop = s_stop-self.step, s_start-self.step

            sliced = True
            cls = type(self)
            return cls(start, stop, step, self.raw_repr, sliced)

        if isinstance(key, int):
            i = int(key)
            if i < 0:
                if self.stop is None:
                    msg = 'Cannot count backward from an Aleph_0 infinite set'
                    raise IndexError(msg)
                if i + self.len() < 0:
                    raise IndexError('eset index out of range')
                i = self.len() + i
            if i >= 0:
                if self.stop is None or i < self.len():
                    return self.internal_direct_function(i)
                raise IndexError('eset index out of range')
        raise ValueError('Need a slice or a positive integer')

    @abc.abstractmethod
    def __contains__(self, val):
        """Conditions to check if value belongs to the eset."""

    @abc.abstractmethod
    def inverse_fun(self, val):
        """The index to return given a value, the inverse function"""

    @abc.abstractmethod
    def direct_function(self, i):
        """The value to return given an index"""

    @abc.abstractmethod
    def stop_init(self, stop=None):
        """Should return the stop value for the eset, it can be either
        a positive integer or a None (in case it is an Infinite eset)
        """
    def internal_direct_function(self, i):
        """The used internal value given an index"""
        return self.direct_function(self.start + i * self.step)

    def internal_inverse_fun(self, val):
        """The used internal index given a value, the inverse"""
        return (self.inverse_fun(val) - self.start) // self.step

    def index(self, val):
        if val not in self:
            sliceStr = '*' if self.sliced else ''
            cls = type(self)
            msg = f'{val!r} not in {cls.__name__}'+sliceStr
            raise ValueError(msg)
        return self.internal_inverse_fun(val)

    def iter_condition(self, i):
        if self.stop is None:
            return True
        else:
            return i < self.len()

    def __iter__(self, i=0):
        while self.iter_condition(i):
            yield self.internal_direct_function(i)
            i += 1

    def clean_class_name(self):
        cls = str(type(self))
        # Hey it works!... ok?! If there are performance issues down
        # the line, for some reason... cause it is mostly for the
        # repr, we'll come back to this.
        return cls[cls.index('.')+1:cls.index('.') +
                   cls[cls.index('.'):].index("'")]

    def __repr__(self):
        max_val = 4
        if not self.raw_repr:
            ellipsis = ', ...'
            try:
                last = min(max_val, self.len())
                if max_val >= self.len():
                    ellipsis = ''
            except ValueError:
                last = max_val
            rstr = ', '.join([str(v) for v in self[:last]])
            rstr += ellipsis
            sliceStr = '*' if self.sliced else ''
            ccls = self.clean_class_name()
            return f'<esets.{ccls}'+sliceStr+f' ({rstr})>'
        else:
            return f'self.start = {self.start},\n' +\
                f'self.stop = {self.stop},\n' +\
                f'self.step = {self.step},\n' +\
                f'self.sliced = {self.sliced},\n' +\
                f'self.raw_repr = {self.raw_repr}'


if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
