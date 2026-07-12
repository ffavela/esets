# Combinatorics on esets (cesets)

This is the eset case study for combinatorics: [cesets.py](cesets.py)
and [lib/ecombinatorics.py](lib/ecombinatorics.py), collectively the
"cesets". Where the rest of this library enumerates numbers,
these enumerate permutations, combinations, arrangements, subsets,
integer partitions, and set partitions, each one addressable by a
single index with no enumeration of anything that comes before it.

Two acknowledgements before diving in. The multiset-counting ideas
behind several of these classes, particularly the memoized recursive
counting and the "capacities can't bind" shortcut used all over
[lib/ecombinatorics.py](lib/ecombinatorics.py), were worked out first
in a sibling project of this one, [mset](https://github.com/ffavela/mset),
which studies multiset combinations and counting on its own. And the general design
philosophy of this whole library, leaning on Python's sequence
protocol so that `__len__`/`__getitem__` (and little else) are enough
to get iteration, slicing, and membership testing for free, owes a
debt to Luciano Ramalho's *Fluent Python*; docTest.txt has a section
demonstrating this directly, feeding the book's own FrenchDeck example
straight into `Distinct_Permutator`.

This file is a curated tour, one section per family, covering the
core idea, the interesting features, and how fast it actually is. It
is not exhaustive: docTest.txt has the full doctest suite for these
classes (order-independence, alphabet, Counter input, reversal
caveats, and every edge case), and is the place to look for detail
this file doesn't cover. For several of these families put to work
together on one running example, see [POKER.md](POKER.md). If you
don't need any of the specific counting algorithms below and just want
to wire up a one-off eset from plain functions instead of writing a
class, see `EMap` in [README.md](README.md).

## A note on speed, upfront

There are two different questions hiding behind "how fast is this",
and it's worth pulling them apart before quoting any complexity at
all, since the answers point in opposite directions.

**Does the cost depend on which index you ask for?** No, not at all,
and this is the part that's genuinely `O(1)`: `direct_function`/
`inverse_function` do exactly the same amount of work whether the
index is 0 or something within a hair of `n! - 1`. Nothing here ever
enumerates the terms before `i` to get to `i`, which is the entire
point of doing this as an eset rather than materializing
`itertools.permutations(...)` and indexing into a list -- that's what
makes `shuffles[10**20]` in docTest.txt come back instantly out of a
`52!`-sized space rather than counting up to it. This isn't just a
design claim; it's checkable: with `n` held fixed, timing
`Natural_Permutator(20)[i]` for `i` at 0, in the middle, and at
`19! - 1` (the far end of a `2.4 * 10**18`-sized space) all land within
the same few microseconds.

**Does the cost depend on `n` (the size of the sequence/integer/set
the eset was built from)?** Yes, and that's the number this file
actually quotes below as "Big O". `n` is fixed at construction time
(`len(elements)` for a `Permutator`, the integer for a `Partitioner`,
...); it isn't something a caller picks per lookup the way the index
is. Every `O(n**2)`-and-up figure in this file is about *this* axis,
never the index. So "random access" and "`O(1)`" are both true of
these classes, but only along the index axis -- along the `n` axis,
where the polynomial complexity actually lives, they behave like any
other ranking algorithm would.

The distinction matters because the simpler esets elsewhere in this
library (`Evens`, `Wholes`, `Float64s`, ...) are `O(1)` on *both* axes
at once: their `direct_function` is a closed-form formula with no
separate "size" parameter to be polynomial in. The cesets have that
extra parameter, `n`, precisely because ranking/unranking a
combinatorial structure is real algorithmic work in a way that
`2 * i` isn't. Everything below is about that work, not about the
random-access property, which holds unconditionally throughout this
whole file.

Two further caveats apply broadly to the `n`-axis cost, found by
actually timing things rather than assuming:

* None of the counting helpers that need real recursion (as opposed to
  a closed form like `math.comb`) share their memo cache across sibling
  branches explored *within* a single `direct_function`/`inverse_function`
  call — each call to a counting helper gets its own fresh cache. The
  practical effect: classes whose counting reduces to `math.factorial`/
  `math.comb`/`math.perm` scale cleanly (roughly `O(n**2)` in informal
  timing); classes that need genuine memoized recursion (multiset
  combinations/arrangements, integer partitions, set partitions) are
  measurably slower in practice than their own state-space size would
  suggest, since overlapping subproblems across different tried
  candidates get recomputed rather than reused.
* These are recursive implementations, not iterative ones, so Python's
  default recursion limit (1000) is a real practical ceiling, and it
  bites at different, sometimes surprisingly modest, sizes for
  different classes -- concrete numbers are called out per section
  below.

Neither caveat is about correctness; every class here is verified
exhaustively against brute-force enumeration for small cases. They're
about where the practical (as opposed to asymptotic) ceiling actually
sits.

## Permutator: arranging everything

`Natural_Permutator(n)` ranks/unranks permutations of `range(n)` via
the factorial number system; `Distinct_Permutator(elements)` wraps it
for real, unique elements. `Natural_Multiset_Permutator`/`Permutator`
generalize both to sequences with repeats, collapsing indistinguishable
rearrangements via the multinomial coefficient instead of counting
`n!` of them:

```python
>>> from cesets import Permutator
>>> banana = Permutator('BANANA')
>>> banana.len()
60
>>> banana[0]
('B', 'A', 'N', 'A', 'N', 'A')
>>>
```

60, not `6! = 720`: the repeated A's and N's collapse rearrangements
that swap two identical letters. `Permutator` also takes an optional
`alphabet` argument (fixing canonical class order independent of how
elements happen to be arranged) and accepts a `Counter`/dict directly
as a histogram. One property doesn't generalize from the no-repeats
case: the last permutation isn't reliably the first one reversed once
elements repeat (docTest.txt has the worked counterexample and the
reason why).

**Speed:** `Natural_Permutator`/`Distinct_Permutator` are the cleanest
of the whole family, `O(n**2)` in practice (each of the `n` unranking
steps does an `O(n)` list operation). `Natural_Multiset_Permutator`/
`Permutator` are the same shape but with a larger constant, since the
multinomial coefficient for the remaining labels gets recomputed at
every step rather than cached across steps.

## Natural_Derangement: permutations with no fixed point

A restriction of `Natural_Permutator`: permutations of `range(n)`
where no position holds its own index, counted by the subfactorial
`!n`. `Distinct_Derangement` wraps it for real, unique elements the
same way `Distinct_Permutator` wraps `Natural_Permutator`:

```python
>>> from cesets import Natural_Derangement
>>> nd = Natural_Derangement(4)
>>> nd.len()
9
>>> nd[0]
(1, 0, 3, 2)
>>>
```

9, not `4! = 24`: every permutation that leaves so much as one element
in place is excluded. Unlike `Natural_Permutator`, this doesn't unrank
one position at a time -- it's the classic two-case bijection behind
`!n = (n-1)*(!(n-1) + !(n-2))`: fix where the smallest remaining label
maps to, then either close it off as a 2-cycle (an ordinary derangement
of everyone else), or build an ordinary derangement of one fewer label
and relabel one of its values to recover the real assignment.

**Speed:** this is the one class in the whole family with a
meaningfully tighter practical ceiling than the rest. The "continue"
case above calls the same unranking routine again, nested, to build
the smaller derangement it relabels -- so stack depth compounds faster
than a single `n`-deep call chain the way every other class here
manages. Concretely: `Natural_Derangement(59)` unranks fine,
`Natural_Derangement(60)` hits Python's default recursion limit, in
informal testing. Comfortably enough for a deck-sized derangement, not
enough to treat this one as scaling the way its siblings do.

## Combinator: choosing, order doesn't matter

`Natural_Combinator(n, k)` is the classic `comb(n, k)`; `Combinator`
generalizes it to choosing `k` from a multiset, using the mset-derived
counting:

```python
>>> from cesets import Combinator
>>> c = Combinator(['a', 'a', 'b'], 2)
>>> list(c)
[('a', 'a'), ('a', 'b')]
>>>
```

Only 2, not `comb(3, 2) = 3`: choosing either of the two physical a's
is the same choice. Unlike the permutators, a combination is
inherently unordered, so `contains()`/`index()` here accept any
ordering of a valid selection and rank it the same way.

**Speed:** `Natural_Combinator` reduces to `math.comb`-based
arithmetic and scales cleanly. `Natural_Multiset_Combinator` is the
one that most needed mset's own memoized-recursion trick, and it
shows: it's measurably slower in practice than `Natural_Combinator`
at comparable sizes (thousands of times slower at a few hundred
classes in informal timing, versus tens of times for the plain case)
because of the per-call cache issue described above, and it hits
Python's recursion limit somewhere around 250-300 classes at small
capacities. Fine for realistic inputs; worth knowing before reaching
for a multiset combinator with hundreds of distinct classes.

## Arranger: choosing *and* arranging

`Arranger` sits between the two: choose `r` elements and arrange them,
i.e. nPr generalized to multisets. It's conceptually the same result
you'd get composing a `Combinator` (which r) with a `Permutator` for
each choice, computed directly instead:

```python
>>> from cesets import Arranger
>>> arr = Arranger(['a', 'a', 'b'], 2)
>>> list(arr)
[('a', 'a'), ('a', 'b'), ('b', 'a')]
>>>
```

Order matters again here, so `('a', 'b')` and `('b', 'a')` are both
present and distinct, unlike `Combinator`.

**Speed:** `Natural_Arranger` (no repeats) is `O(n**2)`-clean, the
same shape as `Natural_Permutator`. `Natural_Multiset_Arranger` shares
`Natural_Multiset_Combinator`'s per-call caching caveat, since its own
counting function has the same recursive shape.

## Powerset: every size at once

`Combinator` fixes `k`; `Powerset` varies over every `k` from 0 to `n`
at once, in graded order (all size-0 subsets, then all size-1, and so
on), reusing `Natural_Combinator`/`Natural_Multiset_Combinator`
directly for each size-block:

```python
>>> from cesets import Powerset
>>> ps = Powerset(['a', 'a', 'b'])
>>> list(ps)
[(), ('a',), ('b',), ('a', 'a'), ('a', 'b'), ('a', 'a', 'b')]
>>>
```

Counting needs no recursion at all here, a first among this family:
`Natural_Powerset`'s count is just `2**n`, and the multiset version's
is `product(c + 1 for c in capacities)`, since each class
independently contributes anywhere from 0 up to its own capacity.

**Speed:** `Natural_Powerset` is as clean as `Natural_Combinator`
(it delegates to it after a small `O(n)` step to find which
size-block an index falls in). `Natural_Multiset_Powerset` inherits
`Natural_Multiset_Combinator`'s caveat the same way, since it
delegates to that once the block is found.

## Partitioner: writing a number as a sum

Integer partitions: every way to write `n` as a sum of positive
integers, order disregarded, no elements domain involved at all:

```python
>>> from cesets import Partitioner
>>> list(Partitioner(5))
[(1, 1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1), (3, 1, 1), (3, 2), (4, 1), (5,)]
>>>
```

Unlike every other class here, there's no `Distinct_`/multiset split:
a partition's parts already are the integers, nothing to translate.
The count, `p(n)`, has no closed form the way `n!`/`comb(n, k)` do;
it's a classic memoized DP (worked through in detail in the
conversation that built this class, and in the docstrings of
`partitions_count`/`get_partition` in
[lib/ecombinatorics.py](lib/ecombinatorics.py)).

**Speed:** the recursion-limit ceiling here is comfortably high for
practical use, somewhere between `n=400` and `n=800` in informal
testing, well past any partition count a person would realistically
enumerate one at a time.

## Compositioner: the same sum, but order counts

`Partitioner` disregards order; `Compositioner` is the sibling that
doesn't, so `4 = 1 + 3` and `4 = 3 + 1` count as two different
compositions, not one:

```python
>>> from cesets import Compositioner
>>> list(Compositioner(5))
[(1, 1, 1, 1, 1), (2, 1, 1, 1), (1, 2, 1, 1), (1, 1, 2, 1), (1, 1, 1, 2), (3, 1, 1), (2, 2, 1), (2, 1, 2), (1, 3, 1), (1, 2, 2), (1, 1, 3), (4, 1), (3, 2), (2, 3), (1, 4), (5,)]
>>>
```

This is the one class in the whole family that needed no new
combinatorics at all: a composition of `n` corresponds exactly to a
subset of the `n-1` gaps between `n` items in a row (does a divider go
there or not), so the count is just `2**(n-1)`, and
`direct_function`/`inverse_function` reuse `get_subset`/
`get_subset_number` directly, the same functions `Natural_Powerset`
itself calls, applied to the complementary "no divider here" gaps.
That complement was chosen deliberately: it's what makes composition
`#0` and the last composition match `Partitioner`'s own convention
(all-ones first, `(n,)` last) at both ends, even though the two
classes enumerate entirely different, differently-sized sets.

**Speed:** as fast as `Natural_Powerset`, since that's exactly what it
delegates to -- no independent recursion-limit ceiling of its own to
report.

## Set_Partitioner: grouping, not summing

The object integer partitions can't express: grouping `n`
*distinguishable* elements into non-empty, unordered blocks, counted
by the Bell numbers rather than `p(n)`. `Natural_Set_Partitioner`
represents each grouping as a restricted growth string; `Set_Partitioner`
translates that into actual groups of elements:

```python
>>> from cesets import Set_Partitioner
>>> list(Set_Partitioner(['a', 'b', 'c']))
[(('a', 'b', 'c'),), (('a', 'b'), ('c',)), (('a', 'c'), ('b',)), (('a',), ('b', 'c')), (('a',), ('b',), ('c',))]
>>>
```

A grouping is unordered twice over (the blocks, and the elements
within each block), so `contains()`/`index()` accept any reshuffling
of either. Elements must be unique, the same requirement
`Distinct_Permutator` has, and for the same reason there's no
`alphabet`/`Counter` support either: grouping is fundamentally about
distinguishable items, so there's no meaningful "repeated element"
variant to disambiguate.

**Speed:** this is the most constrained class in the whole family.
Its restricted-growth-string recursion hits Python's recursion limit
around `n=80`-`100` elements in informal testing, the lowest ceiling
here by a wide margin. Bell numbers grow fast enough that this is
unlikely to matter in practice (`B(80)` is already astronomically
larger than anything you'd enumerate), but it's worth knowing this one
specifically has the tightest practical ceiling of the family.
