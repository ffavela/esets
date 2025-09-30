import pdb

VALUE = 2


class Pairs:
    """Something that contains all positive integer pairs"""
    def __init__(self, start=0, stop=None, step=1,
                 flip_step=None, raw_repr=False):
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
        # Keeping track of the step when a flip happens
        self.flip_step = flip_step
        self.raw_repr = raw_repr

    def step_function(self, i: int) -> int:
        """A simple step function"""
        if i == 0:
            return 0
        return 1

    # def __len__(self): # Welp I tried
    #     return int(float('Inf'))

    def __len__(self):
        return self.abs_len()

    def abs_len(self):
        start = self.start
        stop = self.stop
        step = self.step

        if stop is not None:
            delta = stop - start
            # The following makes repr tests to fail we might need to
            # involve a flip variable.
            # if delta >= 0 and step < 0 or\
            #    delta <= 0 and step > 0:
            #     return 0
            delta = abs(delta)
            return self.step_function(delta % step) +\
                delta // abs(step)
        raise ValueError('Aleph_0 infinite')

    def new_len(self, key):
        """Should only be called when there are key slices"""
        a = key.start
        b = key.stop
        # return abs_len()

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start
            kstart = key.start  # this can be modified if negative
            stop = key.stop
            kstop = key.stop  # this can be modified if negative
            step = key.step
            flip = False  # A sign flip tracker for the step
            flip_step = self.flip_step
            # if key.start is None and key.stop is None and key.step == -1\
            #    and self.step == -12:
            #     breakpoint()
            if key.step is None:
                step = self.step
            elif self.step is not None:
                step = self.step * key.step
                flip = True if step * self.step < 0 else False
            else:
                step = 1
            if key.start is None:
                start = self.start
                if self.stop is not None:
                    kstart = self.__len__()-1 if flip else 0
                else:
                    kstart = 0
            if key.start is not None and key.start < 0:
                kstart = self.__len__() + key.start
                if kstart < 0:
                    # Correct later for outbound slice behavior
                    raise IndexError('eset slice out of range')
                # Need to the check self.step < 0 cases
                start = self.start + kstart * self.step

            # if key.step == -1 and self.step == -12 and key.stop == 1:
            #     breakpoint()

            if self.stop is not None:
                if key.stop is not None and key.stop < 0:
                    kstop = self.__len__() + key.stop
                    if kstop < 0:
                        # Correct later for outbound slice behavior
                        raise IndexError('eset slice out of range')

            # # This is testing code. Not sure how to proceed.
            # if key.stop is not None and key.step is not None\
            #    and key.step < 0 and step > 0:
            #     kstop = self.__len__() - 1 - key.stop

            if self.stop is None:
                if step > 0:
                    if key.stop is not None:
                        stop = self.start + kstop * step
                    else:
                        stop = self.stop

            if self.stop is not None:
                if step > 0:
                    if key.stop is not None:
                        if self.step < 0:
                            kstop = self.__len__() - 1 - kstop
                        stop = min(self.start + kstop * self.step,
                                   self.stop)
                    else:
                        stop = self.stop
                # else:  # that is step < 0

                if flip and self.stop is not None:
                    # if self.step == -12:
                    #     breakpoint()
                    if flip_step is None:
                        flip_step = self.step
                    if step > 0:
                        flip_step = -flip_step
                    start = self.stop + (kstart - self.__len__()) * \
                        flip_step
                    extremum = min if step > 0 else max
                    if key.stop is not None:
                        stop = extremum(self.start+kstop*flip_step,
                                        self.start-flip_step)
                    else:
                        stop = self.start - flip_step
                    flip_step = self.step

            if not flip and self.step < 0:
                if self.stop is None:
                    raise ValueError('Cannot reverse an Aleph_0 infinite')
                abstep = -self.step
                if key.start is not None:
                    start = max(self.start+key.start*abstep,
                                self.start)
                else:
                    start = self.start
                stop = max(self.start+key.stop*abstep,
                           self.stop)
            return Pairs(start, stop, step, flip_step,
                         self.raw_repr)

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
            f'obj.step = {obj.step},\n' +\
            f'obj.flip_step = {obj.flip_step}'

if __name__ == '__main__':
    import doctest
    doctest.testfile("pairsDocTest.txt")
    # doctest.testfile("pairsDocTestSmall.txt")
