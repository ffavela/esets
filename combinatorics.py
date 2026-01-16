from eset import Eset
import lib.combinatorics as lc
from math import factorial


class Canonical_Permutator(Eset):
    """A basic eset that handles permutations without repetition"""
    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.VALUE = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            self.VALUE = args[0]
            super().__init__(xtra_params=(self.VALUE,))
        else:
            self.VALUE = 2  # Not sure, may be better to raise error
            super().__init__(*args, xtra_params=(self.VALUE,))

    def direct_function(self, i):
        return lc.get_permutation(i, self.VALUE)

    def inverse_fun(self, val):
        return lc.get_permutation_number(val)

    def stop_init(self):
        return factorial(self.VALUE)

    def __contains__(self, val):
        if not isinstance(val, tuple):
            return False

        restupl = tuple(range(self.VALUE))
        if tuple(sorted(val)) != restupl:
            return False

        return self.simple_contains(val)
