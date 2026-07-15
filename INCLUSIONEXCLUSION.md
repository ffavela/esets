# Inclusion-exclusion: a performance comparison

`Natural_Multiset_Combinator`/`multiset_combination_count`
(see [COMBINATORICS.md](COMBINATORICS.md) and
[esets/ecombinatorics.py](esets/ecombinatorics.py)) count k-combinations
of a multiset whose classes have per-element capacities -- the exact
problem behind the poker hand-shape counting and inventory-basket
examples in [POKER.md](POKER.md). This file solves the identical
problem a second, completely different way -- the inclusion-exclusion
principle -- and benchmarks it head-to-head against the memoized
recursion (DP) this project actually ships. The headline result isn't
"DP always wins": which approach is faster depends on *where* the
capacities live, in a way that adds a genuinely new axis to the
Big-O discussion COMBINATORICS.md already opened.

## The theory

Counting solutions to `x_1 + x_2 + ... + x_m = k` with every `x_i >= 0`
and no upper bound is the standard stars-and-bars result,
`comb(k + m - 1, m - 1)`. Capacities `c_1, ..., c_m` add the
constraint `x_i <= c_i`, and that's exactly what breaks the closed
form: some of the stars-and-bars solutions assign more than `c_i` to
some class, and those need to be subtracted back out.

Inclusion-exclusion does this by summing over every subset `S` of
classes considered "in violation" (`x_i > c_i` for `i` in `S`). For a
fixed `S`, substituting `x_i' = x_i - (c_i + 1)` for `i` in `S` turns
"at least the classes in `S` exceed their cap" into an ordinary,
unbounded stars-and-bars count over a smaller total:

```
N(S) = comb(m - 1 + k - sum((c_i + 1) for i in S), m - 1)
```

(zero whenever that reduced total goes negative -- more was already
demanded of `S` than `k` has to give). Inclusion-exclusion alternates
sign by `|S|` to cancel the overcounting exactly:

```
N(caps, k) = sum((-1)**len(S) * N(S) for S in every subset of the m classes)
```

That's a sum over `2**m` subsets -- exponential in the number of
*classes*, not in `k`, which is the first hint of where this is
going to diverge from the DP.

## A direct implementation

```python
>>> from math import comb
>>> from itertools import combinations
>>> def ie_naive(capacities, k):
...     m = len(capacities)
...     total = 0
...     for r in range(m + 1):
...         sign = -1 if r % 2 else 1
...         for S in combinations(range(m), r):
...             excess = sum(capacities[i] + 1 for i in S)
...             if excess > k:
...                 continue
...             total += sign * comb(m - 1 + k - excess, m - 1)
...     return total
...

```

Checked against the two worked examples already established in this
project: the 8-SKU, 2-in-stock basket count from the "purchase
transaction" discussion, and the 13-rank, capacity-4 poker hand-shape
count from [POKER.md](POKER.md):

```python
>>> from esets import Natural_Multiset_Combinator
>>> ie_naive((2,) * 8, 5)
504
>>> ie_naive((2,) * 8, 5) == Natural_Multiset_Combinator((2,) * 8, 5).len()
True
>>> ie_naive((4,) * 13, 5)
6175
>>> ie_naive((4,) * 13, 5) == Natural_Multiset_Combinator((4,) * 13, 5).len()
True

```

And, more thoroughly, against 200 random `(capacities, k)` inputs:

```python
>>> import random
>>> random.seed(42)
>>> mismatches = []
>>> for _ in range(200):
...     m = random.randint(1, 6)
...     caps = tuple(random.randint(1, 4) for _ in range(m))
...     k = random.randint(0, 10)
...     expected = Natural_Multiset_Combinator(caps, k).len()
...     if ie_naive(caps, k) != expected:
...         mismatches.append((caps, k))
...
>>> mismatches
[]

```

A few edge cases worth pinning down explicitly, since they're easy to
get wrong in an inclusion-exclusion implementation: demanding more
than the total available capacity, a zero-capacity class (out of
stock -- `esets` itself requires positive capacities at construction,
but the formula handles zero cleanly), and `k = 0`:

```python
>>> ie_naive((1, 1, 1), 5)
0
>>> ie_naive((0, 5, 5), 3)
4
>>> ie_naive((5, 5, 5), 0)
1

```

## Pruning the sum

The naive version always visits all `2**m` subsets, even ones whose
excess is already hopeless partway through. Since capacities are
non-negative, once a partial subset's excess exceeds `k`, no superset
of it can bring the excess back down -- the whole branch below it can
be cut:

```python
>>> def ie_pruned(capacities, k):
...     m = len(capacities)
...     total = 0
...     def rec(i, excess, sign):
...         nonlocal total
...         if excess > k:
...             return
...         if i == m:
...             total += sign * comb(m - 1 + k - excess, m - 1)
...             return
...         rec(i + 1, excess, sign)
...         rec(i + 1, excess + capacities[i] + 1, -sign)
...     rec(0, 0, 1)
...     return total
...
>>> ie_pruned((2,) * 8, 5) == ie_naive((2,) * 8, 5) == 504
True
>>> ie_pruned((4,) * 13, 5) == ie_naive((4,) * 13, 5) == 6175
True
>>> all(ie_pruned(caps, k) == ie_naive(caps, k) for caps, k in
...     ((tuple(random.randint(1, 4) for _ in range(random.randint(1, 6))),
...       random.randint(0, 10)) for _ in range(100)))
True

```

## Benchmarks

Two regimes turn out to matter, and they favor opposite algorithms.

**Many tight-capacity classes** (small `c_i`, `m` large): this is the
poker/inventory shape -- lots of distinct classes, each one only
holding a handful of items. `k` classes' worth of excess accumulates
fast, so pruning collapses the `2**m` sum to almost nothing, and the
DP's own "capacities can't bind" shortcut
([esets/ecombinatorics.py:167](esets/ecombinatorics.py)) engages
early too. The plain, unpruned sum is the one that suffers, growing
visibly exponentially in `m`:

```python
>>> import time
>>> from esets.ecombinatorics import multiset_combination_count
>>> caps, k = (2,) * 18, 9
>>> t0 = time.perf_counter(); ie_naive(caps, k); t1 = time.perf_counter()
1481108
>>> t2 = time.perf_counter(); ie_pruned(caps, k); t3 = time.perf_counter()
1481108
>>> t4 = time.perf_counter(); multiset_combination_count(caps, k); t5 = time.perf_counter()
1481108
>>> (t1 - t0) > (t3 - t2) * 50 and (t1 - t0) > (t5 - t4) * 50
True

```

The margin only widens from there (measured once, informally, and
included for scale rather than as anything CI should re-time at this
size -- your machine will differ):

| m  | k  | naive I-E | pruned I-E | DP        |
|----|----|-----------|------------|-----------|
| 10 | 5  | 0.0004s   | 0.00001s   | 0.00009s  |
| 15 | 7  | 0.0137s   | 0.00008s   | 0.00012s  |
| 18 | 9  | 0.1194s   | 0.00050s   | 0.00020s  |
| 20 | 10 | 0.5336s   | 0.00075s   | 0.00023s  |
| 22 | 11 | 2.1373s   | 0.00107s   | 0.00028s  |
| 24 | 12 | 9.4208s   | 0.00755s   | 0.00106s  |

**Few large-capacity classes** (`c_i` large, `m` small): this is the
regime nothing above prepares you for. The DP's recursion branches on
`min(rem[0], remaining_k) + 1` at every state -- a factor that grows
with the *capacity itself*, not just with `m`. COMBINATORICS.md's
"Big-O" discussion is entirely about the class-count axis (`n`,
fixed at construction); it says nothing about capacity magnitude,
because none of its examples push that axis hard. Push it, and the DP
-- not the naive sum -- is the one that blows up:

```python
>>> caps, k = (100,) * 8, 400
>>> t0 = time.perf_counter(); ie_pruned(caps, k); t1 = time.perf_counter()
51396760553461
>>> t2 = time.perf_counter(); multiset_combination_count(caps, k); t3 = time.perf_counter()
51396760553461
>>> (t3 - t2) > (t1 - t0) * 50
True

```

Again, informally, for scale (`multiset_combination_count` is doing
real polynomial-but-capacity-scaled work here, not exploding
combinatorially -- it's just that "polynomial in `m`, `k`, *and*
`min(capacity, k)`" stops being fast once that last factor is in the
hundreds or thousands):

| cap | m | k    | pruned I-E | DP       |
|-----|---|------|------------|----------|
| 50  | 6 | 150  | 0.00002s   | 0.00702s |
| 50  | 8 | 200  | 0.00006s   | 0.01367s |
| 100 | 6 | 300  | 0.00003s   | 0.02610s |
| 100 | 8 | 400  | 0.00008s   | 0.05062s |
| 200 | 6 | 600  | 0.00003s   | 0.10771s |
| 200 | 8 | 800  | 0.00008s   | 0.20907s |

At `m = 16`, `cap = 1000` (well outside anything sane to put in a
doctest), the DP takes upward of 19 seconds against a fraction of a
millisecond for pruned inclusion-exclusion -- a reversal complete
enough that "just use the DP" stops being good advice. (Those DP
figures already include one fix this benchmarking exercise found and
patched directly: `multiset_combination_count`/`multiset_arrangement_count`
had no early exit for outright-impossible states -- `remaining_k`
exceeding what every remaining class combined could still supply --
and would recurse all the way down to discover that instead of
noticing immediately. Cheap to add, and it shaves a meaningful slice
off this regime's worst cases, but it doesn't touch the underlying
`min(capacity, k)`-sized branching factor that dominates here.)

## Takeaway

Neither algorithm dominates; they're fast in complementary regimes,
and the reason traces back to the same idea both docs keep returning
to. The DP is fast exactly when capacities are small relative to `k`
-- the same "capacities can't bind" condition that gives it a
stars-and-bars shortcut in the first place. Pruned inclusion-exclusion
is fast exactly when a handful of classes' capacities are enough to
blow past `k` -- i.e. when *few* classes, regardless of how roomy
each one is, already settle the sum. `esets` ships the DP because its
target use cases (hand shapes, capped inventories, anything modeled
after "many distinct classes, each with a small cap") sit
comfortably in the regime where it wins; a workload with the opposite
shape -- few classes, each with room for hundreds or thousands of
items -- would be better served by inclusion-exclusion, pruned rather
than naive, instead.
