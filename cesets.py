from eset import Eset, EABCMixinFactory
import lib.ecombinatorics as ecomb
from math import factorial


class Natural_Permutator(Eset):
    """A basic eset that handles permutations without repetition"""

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.VALUE = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            if not isinstance(args[0], int) or args[0] < 0:
                raise ValueError('Need a non-negative integer to initialize')
            self.VALUE = args[0]
            super().__init__(xtra_params=(self.VALUE,))
        else:
            raise ValueError('Need a non-negative integer to initialize')

    def direct_function(self, i):
        return ecomb.get_permutation(i, self.VALUE)

    def inverse_function(self, val):
        return ecomb.get_permutation_number(val)

    def stop_init(self):
        return factorial(self.VALUE)

    def contains(self, val):
        if not isinstance(val, tuple):
            return False

        restupl = tuple(range(self.VALUE))
        if tuple(sorted(val)) != restupl:
            return False

        return self.slice_contains(val)


Distinct_PermutatorABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Permutator(1))


class Distinct_Permutator(Distinct_PermutatorABCMixin):
    """An eset of every permutation of a finite sequence of unique
    elements, built via EABCMixinFactory on top of
    Natural_Permutator: Natural_Permutator enumerates the
    positions, this class only translates between positions and the
    elements it was given. The sequence as given is permutation #0.
    An empty sequence is valid too and yields the single trivial
    permutation, the empty tuple.

    Note: element/position lookups go through list.index(), which is
    O(n) per call. Fine while n stays small (n! grows fast enough that
    it usually does), but if this becomes a bottleneck, building an
    elements -> position dict once in __init__ would make
    eset_obj_val/inverse_function/contains_mixin_check O(1) instead.

    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) == 1:
            elements = tuple(args[0])
            if len(set(elements)) != len(elements):
                raise ValueError('Elements must be unique')
            self.elements = elements
            super().__init__(xtra_params=(Natural_Permutator(len(elements)),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, or string) of unique elements'
            )

    def init_check(self):
        return True

    def _pos_to_elems(self, pos_tpl):
        return tuple(self.elements[p] for p in pos_tpl)

    def _elems_to_pos(self, val):
        return tuple(self.elements.index(v) for v in val)

    def direct_function(self, i):
        return self._pos_to_elems(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_pos(val))

    def eset_obj_val(self, val):
        """The tuple of positions (Natural_Permutator's own
        vocabulary) corresponding to a tuple of elements."""
        return self._elems_to_pos(val)

    def get_mix_val(self, val):
        """The tuple of elements corresponding to a
        Natural_Permutator tuple of positions."""
        return self._pos_to_elems(val)

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != len(self.elements):
            return False
        return all(v in self.elements for v in val)

    def __getitem__(self, key):
        """Delegating to eset_obj like EMixinABC, but also carrying
        self.elements along when slicing."""
        if isinstance(key, slice):
            return type(self)(xtra_params=(self.eset_obj[key], self.elements))
        return super().__getitem__(key)
