from eset import Eset
import lib.ecombinatorics as ecomb
from math import factorial


class Canonical_Permutator(Eset):
    """A basic eset that handles permutations without repetition"""

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.VALUE = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            if not isinstance(args[0], int) or args[0] <= 0:
                raise ValueError('Need a positive integer to initialize')
            self.VALUE = args[0]
            super().__init__(xtra_params=(self.VALUE,))
        else:
            raise ValueError('Need a positive integer to initialize')

    def direct_function(self, i):
        return ecomb.get_permutation(i, self.VALUE)

    def inverse_function(self, val):
        return ecomb.get_permutation_number(val)

    def stop_init(self):
        return factorial(self.VALUE)

    def __contains__(self, val):
        if not isinstance(val, tuple):
            return False

        restupl = tuple(range(self.VALUE))
        if tuple(sorted(val)) != restupl:
            return False

        return self.slice_contains(val)
