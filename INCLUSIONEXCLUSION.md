# Inclusion-exclusion: a performance comparison

`Natural_Multiset_Combinator`/`multiset_combination_count`
(see [COMBINATORICS.md](COMBINATORICS.md) and
[esets/ecombinatorics.py](esets/ecombinatorics.py)) count k-combinations
of a multiset whose classes have per-element capacities -- the exact
problem behind the poker hand-shape counting in [POKER.md](POKER.md)
and the shop-inventory counting in
[COMBINATORIALDB.md](COMBINATORIALDB.md). This file solves the identical
problem a second, completely different way -- the inclusion-exclusion
principle -- and benchmarks it head-to-head against the memoized
recursion (DP) this project actually ships. The headline result isn't
"DP always wins": which approach is faster depends on *where* the
capacities live, in a way that adds a genuinely new axis to the
Big-O discussion COMBINATORICS.md already opened. One regime in
particular turned out to favor inclusion-exclusion so consistently
that `multiset_combination_count` now calls it directly for that
shape, rather than losing to it -- called out explicitly below, not
glossed over as still being "the DP" winning on its own.

*(This file went through several rounds of revision as its own
benchmarks turned up real fixes worth making to
`esets/ecombinatorics.py`; what follows reflects where that process
ended up.)*

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

Checked against a small hand-picked inventory (8 SKUs, 2 in stock
each, a 5-item basket -- the same shape
[COMBINATORIALDB.md](COMBINATORIALDB.md) works through as a full
worked example, with an actual shop and actual purchases), and
against the 13-rank, capacity-4 poker hand-shape count from
[POKER.md](POKER.md):

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

Three regimes turn out to matter, and no single algorithm wins all of
them.

**Many tight-capacity classes** (small `c_i`, `m` large): this is the
poker/inventory shape -- lots of distinct classes, each one only
holding a handful of items. `k` classes' worth of excess accumulates
fast, so pruning collapses the `2**m` sum to almost nothing, and the
DP's own "capacities can't bind" shortcut
([esets/ecombinatorics.py:174](esets/ecombinatorics.py)) engages
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

**Few large-capacity classes** (`c_i` large, `m` small): the DP's
recursion branches on `min(rem[0], remaining_k) + 1` at every state, a
factor that grows with the *capacity itself*, not just with `m`;
COMBINATORICS.md's "Big-O" discussion is entirely about the
class-count axis (`n`, fixed at construction) and says nothing about
capacity magnitude, because none of its examples push that axis hard.
Pushing it here would make the DP's own recursion blow up -- except
that `multiset_combination_count` recognizes exactly this shape and
hands the subproblem to inclusion-exclusion internally instead of
continuing to branch. **Be honest about what this means for the
comparison below: it is not two independent algorithms competing.**
The DP, for this specific shape, *is* pruned inclusion-exclusion,
called from inside an `elif`.

```python
>>> caps, k = (100,) * 8, 400
>>> t0 = time.perf_counter(); ie_pruned(caps, k); t1 = time.perf_counter()
51396760553461
>>> t2 = time.perf_counter(); multiset_combination_count(caps, k); t3 = time.perf_counter()
51396760553461
>>> (t3 - t2) < 0.01 and (t1 - t0) < 0.01
True

```

The same configurations, before and after the fix, informally, for
scale:

| cap | m | k   | pruned I-E | DP (before) | DP (now)  |
|-----|---|-----|------------|--------------|-----------|
| 50  | 6 | 150 | 0.00002s   | 0.00702s     | 0.000030s |
| 50  | 8 | 200 | 0.00006s   | 0.01367s     | 0.000062s |
| 100 | 6 | 300 | 0.00003s   | 0.02610s     | 0.000021s |
| 100 | 8 | 400 | 0.00008s   | 0.05062s     | 0.000065s |
| 200 | 6 | 600 | 0.00003s   | 0.10771s     | 0.000019s |
| 200 | 8 | 800 | 0.00008s   | 0.20907s     | 0.000065s |

The dispatch only fires below two thresholds, checked together --
`len(rem) <= 15` classes remaining *and* `min(rem) >= 15` capacity on
all of them
([esets/ecombinatorics.py](esets/ecombinatorics.py), search
`_INCLUSION_EXCLUSION_CLASS_THRESHOLD`). Both matter, not just the
class count: inclusion-exclusion has its own weak spot, independent
of everything above -- a target sitting near *half* of a subproblem's
own total capacity prunes poorly regardless of how large that capacity
is, and its cost climbs with `m` alone (`cap=100`, target at exactly
half: `m=10` in 0.0004s, `m=16` in 0.018s, `m=22` in 1.4s, measured
standalone). 15 was chosen by measuring that exact worst case up to
the boundary and confirming it stays under 10ms there before shipping
the threshold -- not an arbitrary round number.

That boundary is real, and worth being honest about too: push *past*
it -- many large-capacity classes together, not few -- and neither
fix applies. `cap=100`, `m=20` (five past the class-count threshold),
target at half: measured at **5.29 seconds**, because the dispatch
condition correctly declines to fire (`len(rem) = 20 > 15`) and
inclusion-exclusion would be no faster there either, for the reason
in the paragraph above. "Few large-capacity classes" quietly meant
"few enough" all along; this just makes that boundary explicit instead
of implicit.

**Targets near the total capacity** (any capacity shape, `k` close to
`sum(capacities)`): this regime isn't about capacity shape at all --
it's about how little slack is left. Pruned inclusion-exclusion's
cutoff only fires once a partial subset's excess exceeds `k`, and near
the ceiling there's barely any excess to exceed: most subsets stay
under `k` for a long time, so pruning barely narrows the `2**m` sum,
even back in the *many tight-capacity classes* shape that made pruning
so effective above:

```python
>>> caps = (2,) * 16
>>> k = sum(caps) - 4
>>> t0 = time.perf_counter(); ie_pruned(caps, k); t1 = time.perf_counter()
3620
>>> t2 = time.perf_counter(); multiset_combination_count(caps, k); t3 = time.perf_counter()
3620
>>> (t1 - t0) > (t3 - t2) * 50
True

```

Growing `m` at a fixed "4 below the ceiling" target shows pruned
inclusion-exclusion sliding back toward its naive, exponential
behavior, while the DP stays flat (informal, for scale, as above):

| m  | pruned I-E | DP       | ratio    |
|----|------------|----------|----------|
| 12 | 0.00109s   | 0.00012s | 8.8x     |
| 16 | 0.02102s   | 0.00023s | 89.8x    |
| 20 | 0.36899s   | 0.00037s | 1,000x   |
| 24 | 5.91856s   | 0.00043s | 13,779x  |
| 28 | 55.51435s  | 0.00030s | 185,041x |

The DP handles this cleanly: its branch loop in
`multiset_combination_count`/`multiset_arrangement_count`
([esets/ecombinatorics.py:182-185](esets/ecombinatorics.py)) bounds
how many units go to the current class on *both* ends, not just from
above (can't exceed its own capacity or `k`). Near the ceiling, an
upper bound alone isn't enough -- plenty of *low* values are just as
hopeless, since assigning too little to this class leaves too much for
the remaining classes to cover. Bounding the loop on both ends turns
those into branches that are never generated, rather than ones
generated, recursed into, and only then discovered to be dead ends --
the same idea as the impossible-state check above, just applied one
level earlier, before the recursive call instead of at the top of it.

A natural follow-up: since `x_i <-> c_i - x_i` is a bijection between
assignments summing to `k` and ones summing to `sum(capacities) - k`,
`multiset_combination_count(caps, k) == multiset_combination_count(caps, sum(caps) - k)`
holds for every capacity/target pair (checked against 500 random
cases). That means a near-ceiling target can be reframed as a
small-*gap* target, and the very same "capacities can't bind" shortcut
applies to the gap instead of to `k` directly -- one more `elif`
alongside the other two:

```python
>>> caps = (10,) * 300
>>> k = sum(caps) - 3
>>> t0 = time.perf_counter(); multiset_combination_count(caps, k); t1 = time.perf_counter()
4545100
>>> t1 - t0 < 0.01
True

```

300 classes, no recursion at all -- the leftover slack (3) fits inside
a single remaining class's own capacity (10), so the closed form
applies immediately. But it doesn't rescue the *tight*-capacity shape
this section's own table uses: with `capacity=2` and slack `3`, no
single remaining class could ever absorb all of it, so this new
shortcut never fires, and the recursion still has to walk down class
by class until the *original* shortcut eventually catches a shrinking
`remaining_k` -- costing recursion depth proportional to `k /
capacity` regardless. Measured directly, the `(2,) * m` shape starts
raising `RecursionError` (Python's default call-stack limit) somewhere
around `m = 600`, with or without this fix. That's not a new problem --
[COMBINATORICS.md](COMBINATORICS.md) already notes the plain recursion
"hits Python's recursion limit somewhere around 250-300 classes" -- and
the fixes in this file push that ceiling out some without removing it.
Actually closing it for tight capacities would mean escaping Python's
call stack altogether, rewriting the recursion iteratively instead of
recursively: a different, larger change than benchmarking against
inclusion-exclusion set out to make.

## Takeaway

Three of the four fixes below close gaps specific to
*inclusion-exclusion's* pruning, without inclusion-exclusion itself
ever entering `multiset_combination_count`. Pruned inclusion-exclusion
cuts a branch the moment its excess is provably hopeless; the DP now
does the equivalent check on both sides of every branch it would
otherwise generate (rather than one), before generating the branch
(rather than after), and even reframes "almost full" targets as
"barely any gap" ones so the existing shortcut can catch them too.
That's why it wins both the "many tight-capacity classes" regime
(where pruning already had plenty to bite into) and the "target near
the total capacity" regime (where pruning barely bites at all,
regardless of how many classes there are) -- with one caveat: the
gap-reframing fix only helps when the leftover slack fits inside some
single remaining class's own capacity. Combine *tight* capacities with
a near-ceiling target and enough classes (the `(2,) * m` shape above,
past roughly `m = 600`), and the DP still exhausts Python's call
stack, a pre-existing limit none of these three fixes were aimed at
closing.

The fourth fix is different in kind: for "few large-capacity classes,"
the DP doesn't out-compete inclusion-exclusion -- it calls it. If you
can't beat them, join... let them join you ;-)

Below 15 remaining classes with at least 15 capacity apiece, the
branching recursion hands the subproblem straight to pruned
inclusion-exclusion instead of continuing to branch on a
capacity-sized factor it can't shrink any other way. That threshold
is a real, checked boundary, not a suggestion: push past it -- many
large-capacity classes together, not few -- and neither algorithm is
fast, since inclusion-exclusion's own pruning weakens as `m` grows
regardless of capacity size (measured standalone: seconds, not
milliseconds, by `m` in the low twenties for a target near half of a
large total). `esets` ships this hybrid
because its target use cases (hand shapes, capped inventories, high-
stock catalogs kept to a modest number of distinct items) all sit
inside the regimes it now covers outright -- "many distinct classes,
each with a small cap" through the first three fixes, "few classes,
each with plenty of room" through the fourth. A workload that's
genuinely *both* many classes *and* large capacities per class is the
one shape nothing here solves, and would need a different approach
entirely, not just a different choice between these two.

## A related fix, out of scope for the benchmarks above

`get_multiset_combination_number`/`get_multiset_arrangement_number` --
the *ranking* side, `.index()` in `Natural_Multiset_Combinator`/
`Natural_Multiset_Arranger`, not the counting this file benchmarks --
had their own inefficiency, unrelated to inclusion-exclusion: they
call `multiset_combination_count`/`multiset_arrangement_count` once
per candidate tried at every class or position, and each of those
calls used to start its memo over from empty, discarding everything
the previous call in the same ranking had already worked out. Fixed by
threading one shared memo through an entire ranking call instead.

Be precise about what this does and doesn't touch: it's a different
function from the one benchmarked throughout this file, called a
different way. Every `multiset_combination_count(caps, k)` call above
is a single, standalone call with no ranking around it, so this fix
changes none of the numbers in this file -- checked directly, live,
not assumed. Same config as the very first benchmark above, same
result, same order of magnitude for the DP's own time
(`0.00020s` in that table):

```python
>>> caps, k = (2,) * 18, 9
>>> t0 = time.perf_counter(); multiset_combination_count(caps, k); t1 = time.perf_counter()
1481108
>>> t1 - t0 < 0.01
True

```

Where it does matter is exactly this file's own "many tight-capacity
classes" shape, on the ranking side instead of the counting side --
`Natural_Multiset_Combinator`/`Natural_Multiset_Arranger` calling
`.index()` on something built from many small-capacity classes, the
poker/inventory shape `COMBINATORIALDB.md` and `TEXTENCODE.md` both
lean on:

```python
>>> from esets.ecombinatorics import (
...     get_multiset_combination, get_multiset_combination_number,
...     get_multiset_arrangement, get_multiset_arrangement_number,
... )
>>> caps, k = (2,) * 60, 40
>>> combo = get_multiset_combination(0, caps, k)
>>> t0 = time.perf_counter(); get_multiset_combination_number(combo, caps); t1 = time.perf_counter()
0
>>> t1 - t0 < 0.1
True

>>> arr = get_multiset_arrangement(0, caps, k)
>>> t0 = time.perf_counter(); get_multiset_arrangement_number(arr, caps); t1 = time.perf_counter()
0
>>> t1 - t0 < 0.1
True

```

Measured before/after, informally, for scale (same shape as this
file's own many-tight-capacity-classes table, 60 classes instead of
up to 24, ranking instead of counting):

| operation                     | classes | size | before  | after    | speedup |
|--------------------------------|--------:|-----:|--------:|---------:|--------:|
| combination ranking (`k=40`)   |      60 |   40 | 0.150s  | 0.0037s  | ~40x    |
| arrangement ranking (`r=40`)   |      60 |   40 | 2.20s   | 0.0157s  | ~140x   |

The arrangement side wins bigger for the same reason `multiset_arrangement_count`
has fewer shortcuts than `multiset_combination_count` to begin with
(no inclusion-exclusion dispatch, no gap-reframing) -- more of its
work was genuinely redundant recomputation rather than already-pruned
branches, so there was more for a shared memo to save. Neither fix
touches recursion *depth* -- the ceiling `COMBINATORIALDB.md`'s "One
honest boundary" section documents for ranking is still there, and
still a different, larger change than this one.
