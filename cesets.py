from eset import Eset, EABCMixinFactory
import lib.ecombinatorics as ecomb
from math import factorial, comb
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
    distinguishable arrangements of a multiset. Parametrized either by
    the original sequence expressed as canonical labels (small
    integers 0..k-1 for the k distinct classes present, repeats
    allowed), or by a multiplicities tuple, one positive integer count
    per class, optionally followed by a group_order index (default 0)
    selecting which arrangement of the classes themselves (via
    Natural_Permutator) to expand: multiplicities (2, 3, 1) with the
    default group_order expands to labels (0, 0, 1, 1, 1, 2).

    The two forms never collide: a valid canonical labels tuple always
    contains 0 (its distinct values are exactly 0..k-1), while a valid
    multiplicities tuple never does (its entries are strictly
    positive), so a single argument is unambiguous either way.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.LABELS = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) in (1, 2):
            first = tuple(args[0])
            if len(args) == 1 and ecomb.is_canonical_labels(first):
                self.LABELS = first
            else:
                multiplicities = first
                group_order = args[1] if len(args) == 2 else 0
                for count in multiplicities:
                    if not isinstance(count, int) or count <= 0:
                        raise ValueError('Multiplicities must be positive integers')
                group_perm = Natural_Permutator(len(multiplicities))[group_order]
                self.LABELS = tuple(
                    class_id
                    for class_id in group_perm
                    for _ in range(multiplicities[class_id])
                )
            super().__init__(xtra_params=(self.LABELS,))
        else:
            raise ValueError(
                'Need a tuple of canonical labels: 0..k-1, repeats allowed, or'
                ' a multiplicities tuple optionally followed by a group_order'
                ' index'
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


class Natural_Combinator(Eset):
    """A basic eset that handles combinations without repetition: the
    k-subsets of range(n), each represented as an ascending tuple of k
    distinct indices in 0..n-1. Combination #0 is (0, 1, ..., k-1), the
    lexicographically smallest; the count is math.comb(n, k).

    Like every other Natural_* class in this module, value identity
    matters here: only the canonical ascending tuple is a member, a
    differently-ordered tuple of the same indices is not. Order
    independence (any arrangement of a valid choice counts the same)
    is a higher-level concern, handled by Distinct_Combinator and
    Combinator instead, since they're the ones translating to actual,
    order-irrelevant elements.

    Note: like the reversal caveat documented for Permutator, the last
    combination is not generally an order-reversal or complement of
    the first. For n=4, k=2, index 2 is (0, 3) and index 3 is (1, 2):
    complementary under i -> n-1-i, but not reverse-index counterparts
    of one another (that pairing only holds towards the ends).
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.N, self.K = kwargs['xtra_params']
            super().__init__(*args, **kwargs)
        elif len(args) == 2:
            n, k = args
            if not isinstance(n, int) or n < 0 or not isinstance(k, int) or k < 0:
                raise ValueError('Need two non-negative integers: n and k')
            self.N, self.K = n, k
            super().__init__(xtra_params=(self.N, self.K))
        else:
            raise ValueError('Need two non-negative integers: n and k')

    def direct_function(self, i):
        return ecomb.get_combination(i, self.N, self.K)

    def inverse_function(self, val):
        return ecomb.get_combination_number(tuple(sorted(val)), self.N)

    def stop_init(self):
        return comb(self.N, self.K)

    def contains(self, val):
        if not isinstance(val, tuple) or len(val) != self.K:
            return False
        if len(set(val)) != len(val):
            return False
        if any(v < 0 or v >= self.N for v in val):
            return False
        return self.slice_contains(val)


Distinct_CombinatorABCMixin = EABCMixinFactory.create_ABC_mixin(
    Natural_Combinator(1, 0)
)


class Distinct_Combinator(Distinct_CombinatorABCMixin):
    """An eset of every k-combination of a finite sequence of unique
    elements, built via EABCMixinFactory on top of Natural_Combinator:
    Natural_Combinator enumerates the chosen positions, this class
    only translates between positions and the elements it was given.
    Combination #0 is the first k elements, in the order given.

    Like Natural_Combinator, a combination is unordered: contains()
    and index() accept elements in any order, ranking/comparing them
    by the multiset of elements chosen rather than the exact tuple
    given. direct_function always returns elements in the order they
    appear in the original sequence.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.k = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) == 2:
            elements = tuple(args[0])
            k = args[1]
            if len(set(elements)) != len(elements):
                raise ValueError('Elements must be unique')
            if not isinstance(k, int) or k < 0:
                raise ValueError('Need a non-negative integer k')
            self.elements = elements
            self.k = k
            super().__init__(xtra_params=(Natural_Combinator(len(elements), k),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, or string) of unique'
                ' elements, and k'
            )

    def init_check(self):
        return True

    def _pos_to_elems(self, pos_tpl):
        return tuple(self.elements[p] for p in pos_tpl)

    def _elems_to_pos(self, val):
        return tuple(sorted(self.elements.index(v) for v in val))

    def direct_function(self, i):
        return self._pos_to_elems(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_pos(val))

    def eset_obj_val(self, val):
        return self._elems_to_pos(val)

    def get_mix_val(self, val):
        return self._pos_to_elems(val)

    def id_contains(self, val):
        if val == val and Counter(val) != Counter(
            self.direct_function(self.inverse_function(val))
        ):
            return False

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != self.k:
            return False
        return all(v in self.elements for v in val) and len(set(val)) == len(val)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(xtra_params=(self.eset_obj[key], self.elements, self.k))
        return super().__getitem__(key)


class Natural_Multiset_Combinator(Eset):
    """A basic eset that handles combinations with repetition: the
    ways of choosing k elements (canonical labels 0..m-1) from a
    multiset with per-class capacities, given as a multiplicities
    tuple (multiplicities[j] = how many of class j are available).
    Each combination is a non-decreasing tuple of length k. Combination
    #0 greedily takes as many of the smallest class as possible, then
    the next, and so on; the count is multiset_combination_count(
    multiplicities, k), computed with the same memoized recursion (and
    the capacities-can't-bind shortcut) mset uses for multiset
    combination counting.

    Like Natural_Combinator, value identity matters here: only the
    canonical non-decreasing tuple is a member. Order independence is
    handled at the Combinator level instead.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.MULTIPLICITIES, self.K = kwargs['xtra_params']
            super().__init__(*args, **kwargs)
        elif len(args) == 2:
            multiplicities = tuple(args[0])
            k = args[1]
            for count in multiplicities:
                if not isinstance(count, int) or count <= 0:
                    raise ValueError('Multiplicities must be positive integers')
            if not isinstance(k, int) or k < 0:
                raise ValueError('Need a non-negative integer k')
            self.MULTIPLICITIES, self.K = multiplicities, k
            super().__init__(xtra_params=(self.MULTIPLICITIES, self.K))
        else:
            raise ValueError('Need a multiplicities tuple of positive integers, and k')

    def direct_function(self, i):
        return ecomb.get_multiset_combination(i, self.MULTIPLICITIES, self.K)

    def inverse_function(self, val):
        return ecomb.get_multiset_combination_number(
            tuple(sorted(val)), self.MULTIPLICITIES
        )

    def stop_init(self):
        return ecomb.multiset_combination_count(self.MULTIPLICITIES, self.K)

    def contains(self, val):
        if not isinstance(val, tuple) or len(val) != self.K:
            return False
        counts = Counter(val)
        if any(
            c < 0 or c >= len(self.MULTIPLICITIES) or counts[c] > self.MULTIPLICITIES[c]
            for c in counts
        ):
            return False
        return self.slice_contains(val)


CombinatorABCMixin = EABCMixinFactory.create_ABC_mixin(
    Natural_Multiset_Combinator((1,), 0)
)


class Combinator(CombinatorABCMixin):
    """An eset of every k-combination of a finite sequence, repeated
    elements allowed, built via EABCMixinFactory on top of
    Natural_Multiset_Combinator: Natural_Multiset_Combinator enumerates
    the canonical label combinations, this class only translates
    between labels and the elements it was given. Combination #0
    greedily takes as many of the first-appearing element as possible,
    then the next, and so on (or, with an alphabet, by alphabet
    priority instead of first appearance -- see below).

    Unlike Distinct_Combinator, elements need not be unique: choosing
    is capped per distinct value at how many of it are actually
    present, rather than at 1.

    A combination is inherently unordered (unlike a Permutator's
    arrangement): contains() and index() accept any ordering of a
    valid k-element sub-multiset of elements, ranking/comparing them
    by content rather than by the exact tuple given. direct_function
    always returns one canonical order: elements grouped by class,
    classes in canonical order.

    An optional alphabet argument, exactly as for Permutator, fixes
    the canonical class order instead of deriving it from first
    appearance in elements; it must cover every distinct value present
    in elements (extra, unused values are fine), and anything in
    elements missing from alphabet raises a ValueError.

    elements may also be a dict (a Counter, typically): a histogram
    mapping each distinct value to its available count, walked in the
    dict's own iteration order in place of "first appearance in a
    sequence" -- the same convention Permutator uses.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.k, self.classes = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) in (2, 3):
            elements = Permutator._expand_elements(args[0])
            k = args[1]
            if not isinstance(k, int) or k < 0:
                raise ValueError('Need a non-negative integer k')
            self.elements = elements
            self.k = k
            if len(args) == 3:
                alphabet = tuple(args[2])
                if len(set(alphabet)) != len(alphabet):
                    raise ValueError('Alphabet entries must be unique')
                missing = set(elements) - set(alphabet)
                if missing:
                    raise ValueError(
                        f'Elements not present in alphabet: {sorted(missing)}'
                    )
                present = set(elements)
                self.classes = [a for a in alphabet if a in present]
            else:
                self.classes = list(dict.fromkeys(elements))
            multiplicities = tuple(Counter(elements)[c] for c in self.classes)
            super().__init__(
                xtra_params=(Natural_Multiset_Combinator(multiplicities, k),)
            )
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, string, or Counter), k,'
                ' optionally followed by an alphabet'
            )

    def init_check(self):
        return True

    def _labels_to_elems(self, label_tpl):
        return tuple(self.classes[l] for l in label_tpl)

    def _elems_to_labels(self, val):
        return tuple(sorted(self.classes.index(v) for v in val))

    def direct_function(self, i):
        return self._labels_to_elems(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_labels(val))

    def eset_obj_val(self, val):
        return self._elems_to_labels(val)

    def get_mix_val(self, val):
        return self._labels_to_elems(val)

    def id_contains(self, val):
        if val == val and Counter(val) != Counter(
            self.direct_function(self.inverse_function(val))
        ):
            return False

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != self.k:
            return False
        val_counts = Counter(val)
        elem_counts = Counter(self.elements)
        return all(val_counts[v] <= elem_counts.get(v, 0) for v in val_counts)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(
                xtra_params=(self.eset_obj[key], self.elements, self.k, self.classes)
            )
        return super().__getitem__(key)
