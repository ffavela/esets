import abc
import sys


class BEset(abc.ABC):
    """A blind eset, useful believe it or not"""

    def __init__(
        self,
        start=0,
        stop=None,
        step=1,
        raw_repr=False,
        sliced=False,
        xtra_params=(),
    ):
        if not sliced and stop is None:
            stop = self.stop_init()
        if start is None:
            start = 0
        if not isinstance(start, int):
            raise TypeError('Values need to be integers.')
        if not isinstance(step, int):
            raise TypeError('Values need to be integers.')
        if step == 0:
            raise ValueError('slice step cannot be zero')
        if stop is not None:
            if not isinstance(stop, int):
                raise TypeError('Values need to be integers.')
        if start < 0 and stop is None:
            raise ValueError('No last value exists.')
        if stop is not None:
            if stop < start and step > 0 or stop > start and step < 0:
                raise ValueError('Invalid initialization state.')
        else:
            if step < 0:
                raise ValueError('Invalid initialization state.')

        self.start = start
        self.step = step
        self.stop = stop
        self.sliced = sliced
        self.raw_repr = raw_repr
        self.repr_start_max = 4
        self.repr_end_max = 4
        self.xtra_params = xtra_params

    # Explicitly disabling contains because for many besets using an
    # un-optimized contains is effectively the same as not supporting
    # it and I don't want to create false expectations here.
    def __contains__(self, item):
        raise TypeError('Membership check explicitly disabled on besets')

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
            return self.step_function(delta % self.step) + delta // abs(
                self.step
            )
        raise ValueError('Aleph_0 infinite')

    def __getitem__(self, key):
        enum_error = 'Cannot enumerate backward from infinity'
        if isinstance(key, slice):
            if key.start is not None:
                if not isinstance(key.start, int):
                    raise TypeError('slice indices must be integers or None')
            if key.stop is not None:
                if not isinstance(key.stop, int):
                    raise TypeError('slice indices must be integers or None')
            if key.step is not None:
                if not isinstance(key.step, int):
                    raise TypeError('slice indices must be integers or None')
            if key.step == 0:
                raise ValueError('slice step cannot be zero')
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
                if (
                    self.stop is not None
                    and s_stop > self.stop
                    and step > 0
                    and not flip
                ):
                    s_stop = self.stop

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
                elif flip and kstart >= self.len():
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
                if (
                    s_stop < s_start
                    and step > 0
                    or s_stop > s_start
                    and step < 0
                ) and (key.start is not None or key.stop is not None):
                    delta = 0
                else:
                    delta = abs(s_stop - s_start)

                len_raw = delta // abs(self.step) + self.step_function(
                    delta % self.step
                )
                len_step = len_raw // abs(kstep) + self.step_function(
                    len_raw % kstep
                )

                start = s_start
                stop = start + len_step * step

            if flip:
                if self.step < 0:  # step > 0
                    start, stop = s_stop - self.step, s_start - self.step

            sliced = True
            cls = type(self)
            return cls(
                start,
                stop,
                step,
                self.raw_repr,
                sliced,
                xtra_params=self.xtra_params,
            )

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
        raise TypeError('Need a slice or an integer')

    @abc.abstractmethod
    def direct_function(self, i):
        """The value to return given an index"""

    @abc.abstractmethod
    def stop_init(self):
        """Should return the stop value for the eset, it can be either
        a positive integer or a None (in case it is an Infinite eset)
        """

    def internal_direct_function(self, i):
        """The used internal value given an index"""
        return self.direct_function(self.start + i * self.step)

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
        return cls[
            cls.index('.')
            + 1 : cls.index('.')
            + cls[cls.index('.') :].index("'")
        ]

    def format_funct(self, v):
        """A format function intended to be used with the repr"""
        tstr = str(v)
        if isinstance(v, int):
            start_idx = 0
            if v < 0:
                start_idx = 1
            if len(tstr) > 15:
                exp_str = 'e+' + str(len(tstr) - 1 - start_idx)
                tstr = (
                    tstr[: start_idx + 1]
                    + '.'
                    + tstr[start_idx + 1 : 5 + start_idx]
                    + '...'
                    + tstr[-5:]
                    + exp_str
                )
        return tstr

    def __repr__(self):
        ff = self.format_funct
        max_val = self.repr_start_max
        end_max = self.repr_end_max
        tail_str = ''
        if not self.raw_repr:
            ellipsis = ', ...'
            try:
                last = min(max_val, self.len())
                if max_val >= self.len():
                    ellipsis = ''
                if (max_val + 1) == self.len():
                    last = max_val + 1
                    ellipsis = ''
            except ValueError:
                last = max_val
            if self.stop is not None and end_max is not None:
                if end_max < self.len() - last:
                    tail_str = ', '.join([ff(v) for v in self[-end_max:]])
                else:  # that is end_max >= self.len() - last
                    tail_str = ', '.join([ff(v) for v in self[last:]])
                    ellipsis = ''
            rstr = ', '.join([ff(v) for v in self[:last]])
            rstr += ellipsis
            if tail_str != '':
                rstr += ', '
            rstr += tail_str
            sliceStr = '*' if self.sliced else ''
            ccls = self.clean_class_name()
            return f'<esets.{ccls}' + sliceStr + f' ({rstr})>'
        else:
            return (
                f'self.start = {self.start},\n'
                + f'self.stop = {self.stop},\n'
                + f'self.step = {self.step},\n'
                + f'self.sliced = {self.sliced},\n'
                + f'self.raw_repr = {self.raw_repr},\n'
                + f'self.repr_start_max = {self.repr_start_max},\n'
                + f'self.repr_end_max = {self.repr_end_max},\n'
                + f'self.xtra_params = {self.xtra_params}'
            )


class Eset(BEset):
    """With contains and index it can see"""

    def __contains__(self, val):
        if self.contains(val) is False:
            return False
        if self.id_contains(val) is False:
            return False
        return self.slice_contains(val)

    @abc.abstractmethod
    def contains(self, val):
        """Basic conditions to check if value belongs to the eset."""

    @abc.abstractmethod
    def inverse_fun(self, val):
        """The index to return given a value, the inverse function"""

    def internal_inverse_fun(self, val):
        """The used internal index given a value, the inverse"""
        return (self.inverse_fun(val) - self.start) // self.step

    def id_contains(self, val):
        """A check called by __contains__, It performs an identity
        check, meaning that the direct function applied to the inverse
        has to be the same as not applying any operation to a value. A
        kind of trivial check but really important for many cases.

        """
        if val != self.direct_function(self.inverse_fun(val)):
            return False

    def slice_contains(self, val):
        """For __contains__, when slicing is involved."""
        diff = self.inverse_fun(val) - self.start
        if diff % self.step != 0:
            return False
        if self.stop is None:
            if self.start <= self.inverse_fun(val):
                return True
            else:
                return False
        if self.start <= self.inverse_fun(val) < self.stop:
            return True
        if self.stop < self.inverse_fun(val) <= self.start:
            return True
        return False

    def index(self, val):
        if val not in self:
            sliceStr = '*' if self.sliced else ''
            cls = type(self)
            msg = f'{val!r} not in {cls.__name__}' + sliceStr
            raise ValueError(msg)
        return self.internal_inverse_fun(val)


class EMap(Eset):
    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.direct = kwargs['xtra_params'][0]
                self.inverse = kwargs['xtra_params'][1]
                self.contains = kwargs['xtra_params'][2]
                self.base_eset = kwargs['xtra_params'][3]
            super().__init__(*args, **kwargs)
        elif len(args) == 4:
            self.direct = args[0]
            self.inverse = args[1]
            self.contains = args[2]
            self.base_eset = args[3]
            super().__init__(
                xtra_params=(
                    self.direct,
                    self.inverse,
                    self.contains,
                    self.base_eset,
                )
            )
        else:
            raise ValueError('Invalid amount of arguments')
            # super().__init__(*args, xtra_params=(self.VALUE,))

    def contains(self, val):
        return self.contains(val)

    def inverse_fun(self, val):
        return self.inverse(val)

    def direct_function(self, i):
        return self.direct(i)

    def stop_init(self):
        try:
            return self.base_eset.len()
        except ValueError:
            return None
