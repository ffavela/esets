from eset import Eset, EABCMixinFactory
import lib.ecombinatorics as ecomb
from math import factorial, comb, perm
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


class Partitioner(Eset):
    """A basic eset that handles integer partitions: every way of
    writing a non-negative integer n as a sum of positive integers,
    order disregarded. Each partition is represented as a
    non-increasing tuple of positive integers summing to n, the
    standard convention (4 = (3, 1), not (1, 3)).

    Unlike Permutator/Combinator, there's no arbitrary elements domain
    to translate to and from here: a partition's parts already are the
    integers, so this is a single, self-contained class, no Natural_*
    plus wrapper split.

    Partition #0 is (1, 1, ..., 1), n copies of 1; the count grows as
    the largest part is allowed to grow, ending at partition -1, the
    single-part partition (n,). The count itself, p(n), has no
    closed-form shortcut the way n! or comb(n, k) do; it's computed by
    the classic memoized recursion partitions_count(n, m) = partitions
    of n using parts <= m, splitting on whether a part of size m is
    used at all.

    There's no alphabet-equivalent for this class: an alphabet fixes
    an ordering over an arbitrary elements domain, but a partition's
    "elements" are already just sizes. The analogous higher-level
    object, partitioning n actual distinguishable elements into
    non-empty groups (Stirling numbers of the second kind / Bell
    numbers), is a genuinely different combinatorial object and would
    need its own class, not a wrapper on top of this one.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.N = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            if not isinstance(args[0], int) or args[0] < 0:
                raise ValueError('Need a non-negative integer to initialize')
            self.N = args[0]
            super().__init__(xtra_params=(self.N,))
        else:
            raise ValueError('Need a non-negative integer to initialize')

    def direct_function(self, i):
        return ecomb.get_partition(i, self.N)

    def inverse_function(self, val):
        return ecomb.get_partition_number(val, self.N)

    def stop_init(self):
        return ecomb.partitions_count(self.N, self.N)

    def contains(self, val):
        if not isinstance(val, tuple):
            return False
        if any(not isinstance(p, int) or p <= 0 for p in val):
            return False
        if sum(val) != self.N:
            return False
        if list(val) != sorted(val, reverse=True):
            return False
        return self.slice_contains(val)


class Natural_Arranger(Eset):
    """A basic eset that handles arrangements without repetition: the
    ordered ways of choosing r distinct indices from range(n), i.e.
    nPr (n! / (n-r)!), sometimes called partial permutations or
    r-permutations of n. Each arrangement is a tuple of r distinct
    indices in 0..n-1; unlike Natural_Combinator, order matters here,
    so every ordering of a given r-subset is its own distinct member,
    the same "value identity matters" convention as Natural_Permutator.

    Arrangement #0 is (0, 1, ..., r-1); ranking uses the same
    factorial-number-system trick as Natural_Permutator, just stopped
    after r digits instead of continuing through all n, so this class
    reduces to Natural_Permutator exactly when r == n.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.N, self.R = kwargs['xtra_params']
            super().__init__(*args, **kwargs)
        elif len(args) == 2:
            n, r = args
            if not isinstance(n, int) or n < 0 or not isinstance(r, int) or r < 0:
                raise ValueError('Need two non-negative integers: n and r')
            self.N, self.R = n, r
            super().__init__(xtra_params=(self.N, self.R))
        else:
            raise ValueError('Need two non-negative integers: n and r')

    def direct_function(self, i):
        return ecomb.get_arrangement(i, self.N, self.R)

    def inverse_function(self, val):
        return ecomb.get_arrangement_number(val, self.N)

    def stop_init(self):
        return perm(self.N, self.R)

    def contains(self, val):
        if not isinstance(val, tuple) or len(val) != self.R:
            return False
        if len(set(val)) != len(val):
            return False
        if any(v < 0 or v >= self.N for v in val):
            return False
        return self.slice_contains(val)


Distinct_ArrangerABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Arranger(1, 0))


class Distinct_Arranger(Distinct_ArrangerABCMixin):
    """An eset of every way to choose and arrange r elements from a
    finite sequence of unique elements, built via EABCMixinFactory on
    top of Natural_Arranger. Order matters, same convention as
    Distinct_Permutator: a differently-ordered selection of the same
    elements is a different member, not the same one.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.r = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) == 2:
            elements = tuple(args[0])
            r = args[1]
            if len(set(elements)) != len(elements):
                raise ValueError('Elements must be unique')
            if not isinstance(r, int) or r < 0:
                raise ValueError('Need a non-negative integer r')
            self.elements = elements
            self.r = r
            super().__init__(xtra_params=(Natural_Arranger(len(elements), r),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, or string) of unique'
                ' elements, and r'
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
        return self._elems_to_pos(val)

    def get_mix_val(self, val):
        return self._pos_to_elems(val)

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != self.r:
            return False
        return all(v in self.elements for v in val) and len(set(val)) == len(val)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(xtra_params=(self.eset_obj[key], self.elements, self.r))
        return super().__getitem__(key)


class Natural_Multiset_Arranger(Eset):
    """A basic eset that handles arrangements with repetition: the
    ordered ways of choosing r elements (canonical labels 0..m-1) from
    a multiset with per-class capacities. Each arrangement is a tuple
    of length r; order matters, so unlike Natural_Multiset_Combinator,
    every ordering of a given r-element sub-multiset is its own
    distinct member.

    The count has no simple closed form the way nPr or comb(n,k) do:
    it's computed by multiset_arrangement_count(multiplicities, r):
    multiset_arrangement_count(L, r) = sum_x comb(r, x) *
    multiset_arrangement_count(L[1:], r - x), deciding how many of the
    r (still unfilled) slots the current class takes (comb(r, x) ways
    to pick which ones, unrelated to any capacity), then recursing on
    the rest. This is also the total across every
    Natural_Multiset_Combinator combination of size r of that
    combination's own multinomial coefficient, just computed directly
    rather than by enumerating combinations first.

    Ranking/unranking, though, is done one output position at a time
    (mirroring Natural_Multiset_Permutator's place/try_candidate
    exactly, using multiset_arrangement_count as the block size
    instead of multinomial), not class-by-class -- which is what makes
    arrangement #0 agree with Natural_Arranger's ordering when every
    capacity is 1, and with Natural_Multiset_Permutator's ordering
    when r equals the full multiset size.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.MULTIPLICITIES, self.R = kwargs['xtra_params']
            super().__init__(*args, **kwargs)
        elif len(args) == 2:
            multiplicities = tuple(args[0])
            r = args[1]
            for count in multiplicities:
                if not isinstance(count, int) or count <= 0:
                    raise ValueError('Multiplicities must be positive integers')
            if not isinstance(r, int) or r < 0:
                raise ValueError('Need a non-negative integer r')
            self.MULTIPLICITIES, self.R = multiplicities, r
            super().__init__(xtra_params=(self.MULTIPLICITIES, self.R))
        else:
            raise ValueError('Need a multiplicities tuple of positive integers, and r')

    def direct_function(self, i):
        return ecomb.get_multiset_arrangement(i, self.MULTIPLICITIES, self.R)

    def inverse_function(self, val):
        return ecomb.get_multiset_arrangement_number(val, self.MULTIPLICITIES)

    def stop_init(self):
        return ecomb.multiset_arrangement_count(self.MULTIPLICITIES, self.R)

    def contains(self, val):
        if not isinstance(val, tuple) or len(val) != self.R:
            return False
        counts = Counter(val)
        if any(
            c < 0 or c >= len(self.MULTIPLICITIES) or counts[c] > self.MULTIPLICITIES[c]
            for c in counts
        ):
            return False
        return self.slice_contains(val)


ArrangerABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Multiset_Arranger((1,), 0))


class Arranger(ArrangerABCMixin):
    """An eset of every way to choose and arrange r elements from a
    finite sequence, repeated elements allowed, built via
    EABCMixinFactory on top of Natural_Multiset_Arranger. Order
    matters here, same convention as Permutator: a differently-ordered
    selection of the same content is a different member.

    This is the object you'd get by taking a Combinator (choosing
    which r elements, content only) and, for each of its results,
    running a Permutator over that specific selection -- Arranger
    computes the same eventual set directly (and lazily) instead of
    going through that composition, since finding "which combination"
    an index falls under by scanning them would defeat the point of
    an eset.

    An optional alphabet argument works exactly as it does for
    Permutator and Combinator, fixing the canonical class order
    instead of deriving it from first appearance in elements.

    elements may also be a dict (a Counter, typically), exactly as for
    Permutator and Combinator.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.r, self.classes = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) in (2, 3):
            elements = Permutator._expand_elements(args[0])
            r = args[1]
            if not isinstance(r, int) or r < 0:
                raise ValueError('Need a non-negative integer r')
            self.elements = elements
            self.r = r
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
                xtra_params=(Natural_Multiset_Arranger(multiplicities, r),)
            )
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, string, or Counter), r,'
                ' optionally followed by an alphabet'
            )

    def init_check(self):
        return True

    def _labels_to_elems(self, label_tpl):
        return tuple(self.classes[l] for l in label_tpl)

    def _elems_to_labels(self, val):
        return tuple(self.classes.index(v) for v in val)

    def direct_function(self, i):
        return self._labels_to_elems(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_labels(val))

    def eset_obj_val(self, val):
        return self._elems_to_labels(val)

    def get_mix_val(self, val):
        return self._labels_to_elems(val)

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple) or len(val) != self.r:
            return False
        val_counts = Counter(val)
        elem_counts = Counter(self.elements)
        return all(val_counts[v] <= elem_counts.get(v, 0) for v in val_counts)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(
                xtra_params=(self.eset_obj[key], self.elements, self.r, self.classes)
            )
        return super().__getitem__(key)


class Natural_Powerset(Eset):
    """A basic eset that handles the power set of range(n): every
    subset, of every size from 0 to n, 2**n of them in total. Each
    subset is a sorted tuple of distinct indices in 0..n-1.

    Subsets are enumerated in graded order: every subset of size 0
    first, then every subset of size 1, and so on up to size n, with
    each size-k block internally ordered exactly as
    Natural_Combinator(n, k) orders it (indeed, that's exactly what
    this delegates to, using comb(n, k) to find which block an index
    falls in). Subset #0 is always the empty tuple; the last is
    always (0, 1, ..., n-1).

    Like Natural_Combinator, value identity matters here: only the
    canonical sorted tuple is a member. Order independence belongs to
    Distinct_Powerset/Powerset instead.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.N = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            if not isinstance(args[0], int) or args[0] < 0:
                raise ValueError('Need a non-negative integer to initialize')
            self.N = args[0]
            super().__init__(xtra_params=(self.N,))
        else:
            raise ValueError('Need a non-negative integer to initialize')

    def direct_function(self, i):
        return ecomb.get_subset(i, self.N)

    def inverse_function(self, val):
        return ecomb.get_subset_number(val, self.N)

    def stop_init(self):
        return 2**self.N

    def contains(self, val):
        if not isinstance(val, tuple):
            return False
        if len(set(val)) != len(val):
            return False
        if any(v < 0 or v >= self.N for v in val):
            return False
        if list(val) != sorted(val):
            return False
        return self.slice_contains(val)


Distinct_PowersetABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Powerset(0))


class Distinct_Powerset(Distinct_PowersetABCMixin):
    """An eset of every subset of a finite sequence of unique
    elements, of every size, built via EABCMixinFactory on top of
    Natural_Powerset. A subset is unordered, so contains()/index()
    accept any ordering of a valid subset, the same convention
    Distinct_Combinator uses.
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
            super().__init__(xtra_params=(Natural_Powerset(len(elements)),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, or string) of unique elements'
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
        if not isinstance(val, tuple):
            return False
        return all(v in self.elements for v in val) and len(set(val)) == len(val)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(xtra_params=(self.eset_obj[key], self.elements))
        return super().__getitem__(key)


class Natural_Multiset_Powerset(Eset):
    """A basic eset that handles the power set of a multiset with
    per-class capacities: every sub-multiset, of every size, given a
    multiplicities tuple. Each subset is a sorted tuple of canonical
    labels.

    The count needs no recursion at all, unlike every other counting
    function in this module: each class independently contributes
    anywhere from 0 up to its own capacity, so it's a plain mixed-radix
    digit count, multiset_powerset_count(L) = product(c + 1 for c in
    L) -- Natural_Powerset is the special case where every capacity is
    1, reducing this product to 2**n.

    Subsets are enumerated in graded order, exactly as Natural_Powerset
    does: every size-0 sub-multiset first, then every size-1, and so
    on, each size-k block ordered exactly as
    Natural_Multiset_Combinator(multiplicities, k) orders it.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.MULTIPLICITIES = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            multiplicities = tuple(args[0])
            for count in multiplicities:
                if not isinstance(count, int) or count <= 0:
                    raise ValueError('Multiplicities must be positive integers')
            self.MULTIPLICITIES = multiplicities
            super().__init__(xtra_params=(self.MULTIPLICITIES,))
        else:
            raise ValueError('Need a multiplicities tuple of positive integers')

    def direct_function(self, i):
        return ecomb.get_multiset_subset(i, self.MULTIPLICITIES)

    def inverse_function(self, val):
        return ecomb.get_multiset_subset_number(val, self.MULTIPLICITIES)

    def stop_init(self):
        return ecomb.multiset_powerset_count(self.MULTIPLICITIES)

    def contains(self, val):
        if not isinstance(val, tuple):
            return False
        counts = Counter(val)
        if any(
            c < 0 or c >= len(self.MULTIPLICITIES) or counts[c] > self.MULTIPLICITIES[c]
            for c in counts
        ):
            return False
        if list(val) != sorted(val):
            return False
        return self.slice_contains(val)


PowersetABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Multiset_Powerset((1,)))


class Powerset(PowersetABCMixin):
    """An eset of every sub-multiset of a finite sequence, of every
    size, repeated elements allowed, built via EABCMixinFactory on top
    of Natural_Multiset_Powerset the same way Combinator wraps
    Natural_Multiset_Combinator. A subset is inherently unordered:
    contains()/index() accept any ordering of a valid sub-multiset of
    elements, same convention as Combinator.

    An optional alphabet argument works exactly as it does for
    Permutator/Combinator/Arranger. elements may also be a dict (a
    Counter, typically), exactly as for the others.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs and len(kwargs['xtra_params']) != 0:
            eset_obj, self.elements, self.classes = kwargs['xtra_params']
            super().__init__(xtra_params=(eset_obj,))
        elif len(args) in (1, 2):
            elements = Permutator._expand_elements(args[0])
            self.elements = elements
            if len(args) == 2:
                alphabet = tuple(args[1])
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
            super().__init__(xtra_params=(Natural_Multiset_Powerset(multiplicities),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, string, or Counter),'
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
        if not isinstance(val, tuple):
            return False
        val_counts = Counter(val)
        elem_counts = Counter(self.elements)
        return all(val_counts[v] <= elem_counts.get(v, 0) for v in val_counts)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(
                xtra_params=(self.eset_obj[key], self.elements, self.classes)
            )
        return super().__getitem__(key)


class Natural_Set_Partitioner(Eset):
    """A basic eset that handles set partitions: every way of
    grouping range(n) into non-empty, unordered, disjoint blocks whose
    union is everything, counted by the Bell number B(n). Unlike every
    other Natural_* class in this module, elements here are never
    repeated or chosen from a capacity -- a set partition is
    fundamentally about grouping distinguishable positions, so there's
    no Distinct_/Multiset_ split, just this and Set_Partitioner.

    Each partition is represented as a restricted growth string (RGS):
    a tuple a_0..a_{n-1} where a_0 == 0 and each subsequent a_i is at
    most one more than the running maximum of what came before --
    the standard bijective encoding, where block labels are introduced
    in order of first appearance. Partition #0 is (0, 0, ..., 0), one
    block holding everything; the last is (0, 1, 2, ..., n-1), every
    position its own singleton block.

    The count has no closed form: B(n) = set_partition_count(n-1, 1),
    a recursion on "how many ways to extend a RGS with m blocks
    already established, for r more positions" -- at each position,
    join one of the m existing blocks or start a new one (m+1
    choices), recursing on the result. Ranking/unranking follows the
    same place/try_candidate shape as the rest of this module, just
    with m+1 candidates per position instead of a fixed alphabet.
    """

    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.N = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            if not isinstance(args[0], int) or args[0] < 0:
                raise ValueError('Need a non-negative integer to initialize')
            self.N = args[0]
            super().__init__(xtra_params=(self.N,))
        else:
            raise ValueError('Need a non-negative integer to initialize')

    def direct_function(self, i):
        return ecomb.get_set_partition(i, self.N)

    def inverse_function(self, val):
        return ecomb.get_set_partition_number(val)

    def stop_init(self):
        return 1 if self.N == 0 else ecomb.set_partition_count(self.N - 1, 1)

    def contains(self, val):
        if not isinstance(val, tuple) or len(val) != self.N:
            return False
        if not ecomb.is_valid_rgs(val):
            return False
        return self.slice_contains(val)


Set_PartitionerABCMixin = EABCMixinFactory.create_ABC_mixin(Natural_Set_Partitioner(0))


class Set_Partitioner(Set_PartitionerABCMixin):
    """An eset of every way to partition a finite sequence of unique
    elements into non-empty, unordered groups, built via
    EABCMixinFactory on top of Natural_Set_Partitioner: that class
    enumerates restricted growth strings over positions, this class
    only translates between an RGS and the actual groups of elements
    it was given, elements sharing a label going into the same group,
    in label order (0, 1, 2, ... -- the order those groups first
    appear scanning elements left to right).

    A set partition is unordered at two levels -- the groups
    themselves, and the elements within each group -- so
    contains()/index() accept any reordering of either and rank it the
    same, normalizing by re-deriving the RGS a given grouping implies
    (which element ends up in which position-label) rather than
    requiring the exact grouping/ordering direct_function happens to
    produce.

    Elements must be unique, the same requirement Distinct_Permutator
    and friends have, since a set partition is fundamentally about
    grouping distinguishable items -- there's no meaningful analogue
    of "repeated elements" the way Permutator/Combinator/Arranger/
    Powerset have one, so unlike those, there's no alphabet argument
    or Counter/dict input here either: with elements already forced
    unique, first-appearance order is unambiguous on its own.
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
            super().__init__(xtra_params=(Natural_Set_Partitioner(len(elements)),))
        else:
            raise ValueError(
                'Need a finite sequence (list, tuple, or string) of unique elements'
            )

    def init_check(self):
        return True

    def _rgs_to_blocks(self, rgs):
        blocks = {}
        for pos, label in enumerate(rgs):
            blocks.setdefault(label, []).append(self.elements[pos])
        return tuple(tuple(blocks[label]) for label in sorted(blocks))

    def _elems_to_rgs(self, val):
        elem_to_block_id = {}
        for block_id, block in enumerate(val):
            for e in block:
                elem_to_block_id[e] = block_id
        label_map = {}
        rgs = []
        for e in self.elements:
            block_id = elem_to_block_id[e]
            if block_id not in label_map:
                label_map[block_id] = len(label_map)
            rgs.append(label_map[block_id])
        return tuple(rgs)

    def direct_function(self, i):
        return self._rgs_to_blocks(self.eset_obj[i])

    def inverse_function(self, val):
        return self.eset_obj.index(self._elems_to_rgs(val))

    def eset_obj_val(self, val):
        return self._elems_to_rgs(val)

    def get_mix_val(self, val):
        return self._rgs_to_blocks(val)

    def id_contains(self, val):
        canonical = self.direct_function(self.inverse_function(val))
        if val == val and set(frozenset(b) for b in val) != set(
            frozenset(b) for b in canonical
        ):
            return False

    def contains_mixin_check(self, val):
        if not isinstance(val, tuple):
            return False
        if not all(isinstance(b, tuple) and len(b) > 0 for b in val):
            return False
        all_elems = [e for b in val for e in b]
        if len(set(all_elems)) != len(all_elems):
            return False
        return set(all_elems) == set(self.elements)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(xtra_params=(self.eset_obj[key], self.elements))
        return super().__getitem__(key)
