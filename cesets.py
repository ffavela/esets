from eset import Eset, EABCMixinFactory
import lib.ecombinatorics as ecomb
from math import factorial
from collections import Counter


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


class Natural_Multiset_Permutator(Eset):
    """A basic eset that handles permutations with repetition: the
    distinguishable arrangements of a multiset. Parametrized by the
    original sequence expressed as canonical labels (small integers
    0..k-1 for the k distinct classes present, repeats allowed)."""

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.LABELS = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            labels = tuple(args[0])
            if not ecomb.is_canonical_labels(labels):
                raise ValueError(
                    'Need a tuple of canonical labels: 0..k-1, repeats allowed'
                )
            self.LABELS = labels
            super().__init__(xtra_params=(self.LABELS,))
        else:
            raise ValueError(
                'Need a tuple of canonical labels: 0..k-1, repeats allowed'
            )

    def direct_function(self, i):
        return ecomb.get_multiset_permutation(i, self.LABELS)

    def inverse_function(self, val):
        return ecomb.get_multiset_permutation_number(val, self.LABELS)

    def stop_init(self):
        return ecomb.multinomial(Counter(self.LABELS))

    def contains(self, val):
        if not isinstance(val, tuple):
            return False

        if Counter(val) != Counter(self.LABELS):
            return False

        return self.slice_contains(val)


PermutatorABCMixin = EABCMixinFactory.create_ABC_mixin(
    Natural_Multiset_Permutator((0,))
)


class Permutator(PermutatorABCMixin):
    """An eset of every distinguishable permutation of a finite
    sequence, repeated elements allowed, built via EABCMixinFactory on
    top of Natural_Multiset_Permutator: Natural_Multiset_Permutator
    enumerates the canonical labels, this class only translates
    between labels and the elements it was given. The sequence as
    given is permutation #0. An empty sequence is valid too and yields
    the single trivial permutation, the empty tuple.

    Unlike Distinct_Permutator, elements need not be unique: the count
    is the multinomial coefficient n!/(m1!*m2!*...*mk!) rather than
    n!, so repeated elements collapse indistinguishable rearrangements
    into a single entry instead of counting them separately.

    An optional second argument, alphabet, fixes the canonical class
    order instead of deriving it from first appearance in elements.
    alphabet must contain every distinct value present in elements
    (it may also contain extra, unused values); anything in elements
    missing from alphabet raises a ValueError. Supplying an alphabet
    changes what permutation #0 means: instead of "elements exactly as
    given", it becomes "elements sorted by alphabet priority", which
    is what makes the resulting enumeration depend only on the
    alphabet and the multiset, not on the arrangement elements
    happened to be given in.

    elements may also be a dict (a Counter, typically): a histogram
    mapping each distinct value to its multiplicity, walked in the
    dict's own iteration order in place of "first appearance in a
    sequence". Every value must be a positive integer; anything else
    raises a ValueError. Everything downstream, alphabet included,
    works the same either way, since the histogram is expanded into a
    plain tuple before any of that logic runs.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.classes = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) == 1:
            elements = self._expand_elements(args[0])
            self.elements = elements
            self.classes = list(dict.fromkeys(elements))
            labels = tuple(self.classes.index(e) for e in elements)
            super().__init__(xtra_params=(Natural_Multiset_Permutator(labels),))
        elif len(args) == 2:
            elements = self._expand_elements(args[0])
            alphabet = tuple(args[1])
            if len(set(alphabet)) != len(alphabet):
                raise ValueError('Alphabet entries must be unique')
            missing = set(elements) - set(alphabet)
            if missing:
                raise ValueError(f'Elements not present in alphabet: {sorted(missing)}')
            self.elements = elements
            present = set(elements)
            self.classes = [a for a in alphabet if a in present]
            labels = tuple(sorted(self.classes.index(e) for e in elements))
            super().__init__(xtra_params=(Natural_Multiset_Permutator(labels),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, string, or Counter),'
                ' optionally followed by an alphabet'
            )

    def init_check(self):
        return True

    @staticmethod
    def _expand_elements(source):
        if isinstance(source, dict):
            for count in source.values():
                if not isinstance(count, int) or count <= 0:
                    raise ValueError('Counter/dict values must be positive integers')
            return tuple(key for key, count in source.items() for _ in range(count))
        return tuple(source)

    def _labels_to_elems(self, label_tpl):
        return tuple(self.classes[l] for l in label_tpl)

    def _elems_to_labels(self, val):
        return tuple(self.classes.index(v) for v in val)

    def direct_function(self, i):
        return self._labels_to_elems(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_labels(val))

    def eset_obj_val(self, val):
        """The tuple of canonical labels (Natural_Multiset_Permutator's
        own vocabulary) corresponding to a tuple of elements."""
        return self._elems_to_labels(val)

    def get_mix_val(self, val):
        """The tuple of elements corresponding to a
        Natural_Multiset_Permutator tuple of canonical labels."""
        return self._labels_to_elems(val)

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != len(self.elements):
            return False
        return Counter(val) == Counter(self.elements)

    def __getitem__(self, key):
        """Delegating to eset_obj like EMixinABC, but also carrying
        self.elements/self.classes along when slicing."""
        if isinstance(key, slice):
            return type(self)(
                xtra_params=(self.eset_obj[key], self.elements, self.classes)
            )
        return super().__getitem__(key)
