# Arrangement information: when order costs more than choice

POKER.md already showed the two halves of an arrangement: choosing 5
cards out of 52 is a `Distinct_Combinator`, ordering that choice is
what a `Distinct_Permutator` would add on top, and `Distinct_Arranger`
does both at once. For a 5-card hand, most of that arrangement's
information turns out to be "which cards" -- POKER.md's whole
combination-index trick rests on that being true. It stops being true
somewhere between a 5-card hand and a full 52-card shuffle: a full
shuffle carries zero "which cards" information (there's only one way
to grab all 52) and all of it is "in what order". This file finds
exactly where the balance flips, and how that flip point scales with
deck size in general.

*(A worked example that stands on its own -- it doesn't require
having read POKER.md first, though the deck it starts from is the
same one.)*

## The exact split

`Distinct_Arranger` (order-sensitive picks, no repeats) is a
`Distinct_Combinator` times a `Distinct_Permutator`-sized factor:
picking which `k` items, then picking one of `k!` orderings for them.
That's not just true of the counts, it's true bit for bit, because
`log2` turns a product into a sum:

```python
>>> from esets import Distinct_Arranger, Distinct_Combinator
>>> from math import log2, factorial
>>> items = list(range(52))
>>> for k in (5, 16, 52):
...     a = Distinct_Arranger(items, k)
...     c = Distinct_Combinator(items, k)
...     assert a.len() == c.len() * factorial(k)
...     print(k, round(log2(a.len()), 6), round(log2(c.len()) + log2(factorial(k)), 6))
...
5 28.216394 28.216394
16 87.486674 87.486674
52 225.581003 225.581003

```

(Rounded rather than compared to full float precision: `log2(a.len())`
and `log2(c.len()) + log2(factorial(k))` reach the same value by two
different chains of floating-point operations, and those chains don't
always land on the exact same last bit -- a small, harmless reminder
that floats are approximate even when the underlying identity is
exact, distinct from the much larger int-to-float precision loss
TEXTENCODE.md's own precision section demonstrates.)

`log2(a.len())` is the total information content of an arrangement:
however many bits it takes to name one specific ordered pick out of
all possible ones. That total is always exactly `log2(c.len())` (the
"which items" bits) plus `log2(factorial(k))` (the "what order" bits)
-- an identity, not an approximation, so asking which half is bigger
is a real question with a real answer, not a fuzzy one.

## Where it flips, for a 52-card deck

At `k=5` the combination half dominates heavily -- that's the whole
reason POKER.md's combination-index trick is worth doing. At `k=52`
the combination half is zero (there's exactly one way to choose all
52 cards) and the permutation half carries everything. Somewhere in
between, the two swap places:

```python
>>> n = 52
>>> log2fact = [0.0]
>>> for i in range(1, n + 1):
...     log2fact.append(log2fact[-1] + log2(i))
...
>>> def log2_comb(n, k):
...     return log2fact[n] - log2fact[k] - log2fact[n - k]
...
>>> combination_bits = [log2_comb(n, k) for k in range(n + 1)]
>>> permutation_bits = [log2fact[k] for k in range(n + 1)]
>>> flip = next(k for k in range(1, n + 1) if permutation_bits[k] >= combination_bits[k])
>>> flip
16
>>> round(combination_bits[15], 2), round(permutation_bits[15], 2)
(42.03, 40.25)
>>> round(combination_bits[16], 2), round(permutation_bits[16], 2)
(43.24, 44.25)

```

`log2fact` is built once as a running sum rather than by calling
`factorial(k)` and converting it to a float afterward, for the same
reason TEXTENCODE.md's precision section flags: a running sum of
`log2(i)` never routes through `factorial(52)` (or, in the next
section, `factorial(100000)`) as an intermediate value that then has
to survive a lossy `float()` conversion -- it accumulates the
logarithm directly, so there's nothing large to lose precision on.

At `k=15`, combination bits (42.03) still edge out permutation bits
(40.25); by `k=16`, permutation bits (44.25) have pulled ahead of
combination bits (43.24) and never fall back, since `C(n,k)` is
already past its own peak (which sits at `k=n/2=26` by symmetry) while
`k!` keeps compounding all the way to `k=n`. A 5-card poker hand, at
`k=5`, sits well inside the combination-dominated region -- eleven
cards short of the flip.

## The general relationship: k_flip is roughly e times sqrt(n)

Fixing `n=52` and asking "which `k`" is one question; asking how that
flip point moves as the deck itself grows is a different one. It has
a clean closed-form answer.

For `k` small relative to `n`, `C(n,k) = n!/(k!(n-k)!)` is well
approximated by `n**k / factorial(k)` (the top of the fraction is
`k` shrinking terms starting at `n`, each close to `n` itself when
`k << n`). Substituting that into the flip condition
`log2(factorial(k)) = log2(C(n,k))`:

```
log2(k!) ~= log2(n**k / k!)
log2(k!) ~= k*log2(n) - log2(k!)
2*log2(k!) ~= k*log2(n)
log2(k!) ~= (k/2)*log2(n)
```

and Stirling's approximation (`log2(k!) ~= k*log2(k) - k*log2(e)`)
turns the left side into something solvable for `k`:

```
k*log2(k) - k*log2(e) ~= (k/2)*log2(n)
log2(k) - log2(e) ~= (1/2)*log2(n)
log2(k) ~= (1/2)*log2(n) + log2(e)
k ~= e * sqrt(n)
```

`e` falls straight out of the algebra as `2**log2(e)`, not something
fitted after the fact. That predicts a flip point that grows with the
*square root* of the deck size -- doubling `n` should move `k_flip` by
a factor of `sqrt(2) ~= 1.41`, not 2:

```python
>>> from math import e, sqrt
>>> round(e * sqrt(52), 1)
19.6

```

19.6 versus the true `flip = 16` for `n=52` is in the right
neighborhood but not exact, because the approximation leaned on
`k << n`, and 16 isn't all that small next to 52 -- the derivation
should get tighter as `n` grows and `k_flip` becomes a genuinely
smaller fraction of `n`. Checking that against exact crossover points
computed the same running-sum way, for `n` large enough that
`factorial(n)` itself would be an enormous intermediate value even
before any precision is at stake:

```python
>>> def crossover(n):
...     table = [0.0]
...     for i in range(1, n + 1):
...         table.append(table[-1] + log2(i))
...     for k in range(1, n + 1):
...         if table[k] >= table[n] - table[k] - table[n - k]:
...             return k
...
>>> for test_n in (1000, 2000, 5000, 10000, 20000, 50000, 100000):
...     k_flip = crossover(test_n)
...     estimate = e * sqrt(test_n)
...     print(test_n, k_flip, round(estimate, 1), round(k_flip / estimate, 4))
...
1000 82 86.0 0.9539
2000 117 121.6 0.9624
5000 187 192.2 0.9729
10000 267 271.8 0.9822
20000 379 384.4 0.9859
50000 602 607.8 0.9904
100000 854 859.6 0.9935

```

The ratio climbs steadily toward 1 as `n` grows, which is exactly the
"should get tighter" prediction confirmed rather than assumed.

## Is this a known result?

Not as far as a real search turned up. `P(n,k) = C(n,k) * k!` and
Stirling's approximation are both entirely standard, but the specific
question this file asks -- not "which is bigger, P or C" (P is always
at least as big, trivially, by exactly a factor of `k!`) but "where
does `k!`'s own bit-content overtake `C(n,k)`'s" -- didn't turn up a
named theorem, a paper, or a textbook exercise under any phrasing
tried. The `e * sqrt(n)` shape has the same square-root flavor as
other crossover points that show up elsewhere in combinatorics
(birthday-paradox collisions, the ~`2*sqrt(n)` longest-increasing-
-subsequence result), but that's a family resemblance worth noting,
not a citation -- those are different mechanisms answering different
questions. Treat the derivation above as done here, not sourced from
somewhere else.

## One honest boundary

Everything above is about plain `P(n,k)`: order-sensitive picks from
`n` *distinct* items, no repeats, exactly what `Distinct_Arranger`
enumerates. It is not the multiset-capacity-bounded question this
project's own `Natural_Multiset_Arranger` actually ranks (the one
POKER.md's multi-deck section and TEXTENCODE.md's word alphabets both
lean on) -- there, the "what order" factor for a chosen basket of
classes isn't `k!`, it's the multinomial coefficient over the class
counts within that basket (fewer distinct orderings whenever a basket
repeats a class), so the flip point for that version is a genuinely
separate derivation, not a drop-in substitution of `k!` above. Left
here as a clearly scoped follow-up rather than folded into this file.
