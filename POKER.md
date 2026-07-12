# Poker: a worked example

Disclaimer: this is meant to be simply an academic study of the game,
given its popularity and its close relationship to combinatorics and
probability theory. Not playing advice in any way; if you are willing
to bet using advice from some random person on the internet then you
should probably re-evaluate your life's choices.

## A shuffle is just a number

We can start with a French deck example, straight out of
[COMBINATORICS.md](COMBINATORICS.md)'s own FrenchDeck (which itself
comes from Fluent Python): 52 cards, and `Distinct_Permutator(deck)`
gives every one of its `52!` possible shufflings, each addressable by
a single index.

Shuffling can equivalently be seen as choosing a random integer from 0
to `factorial(52) - 1`:

```python
>>> import collections, random
>>> from math import factorial
>>> from cesets import Distinct_Permutator
>>> Card = collections.namedtuple('Card', ['rank', 'suit'])
>>> class FrenchDeck:
...     ranks = [str(n) for n in range(2, 11)] + list('JQKA')
...     suits = 'spades diamonds clubs hearts'.split()
...     def __init__(self):
...         self._cards = [Card(rank, suit) for suit in self.suits
...                                          for rank in self.ranks]
...     def __len__(self):
...         return len(self._cards)
...     def __getitem__(self, position):
...         return self._cards[position]
...
>>> deck = FrenchDeck()
>>> shuffles = Distinct_Permutator(deck)
>>> shuffles.len() == factorial(52)
True

```

(Seeding `random` below so this file's own doctests stay reproducible
-- in a real shuffle you'd just call `random.randint(0, shuffles.len() - 1)`
with no seed at all.)

```python
>>> random.seed(2026)
>>> s = random.randint(0, shuffles.len() - 1)
>>> shuffle = shuffles[s]
>>> s == shuffles.index(shuffle)
True

```

`s` is a single integer standing in for one specific, fully
determined ordering of all 52 cards, and it round-trips exactly, the
same guarantee `docTest.txt` demonstrates for the plain `shuffles`
example. No cards were dealt, shuffled, or even represented as a list
to get here; `s` *is* the shuffle.

## From a shuffle to a hand, and a smaller number for it

A particular hand is just the first 5 cards of that shuffle:

```python
>>> hand = shuffle[:5]
>>> hand
(Card(rank='3', suit='clubs'), Card(rank='4', suit='spades'), Card(rank='3', suit='hearts'), Card(rank='A', suit='hearts'), Card(rank='A', suit='spades'))

```

And a hand, taken on its own, is exactly what `Distinct_Arranger`
enumerates: choosing and arranging 5 cards out of 52 (nPr, not
`shuffles`' full nPn). We can find this hand's own index in that much
smaller space:

```python
>>> from cesets import Distinct_Arranger
>>> arrangements = Distinct_Arranger(deck, 5)
>>> arrangements.len()
311875200
>>> a = arrangements.index(hand)
>>> arrangements[a] == hand
True

```

`a` is a different, much smaller number from `s` -- it only has to
distinguish among `52*51*50*49*48` possible 5-card deals, not among
all `52!` possible full shuffles.

## Order doesn't matter to the game, so why pay for it?

Here's the thing though: whichever hand you're dealt, the order those
5 cards arrived in is not information the game cares about at all --
only *which* cards you're holding matters. Representing a hand as a
list (or as the arrangement index `a` above) keeps that ordering
around anyway, since ordering is implicit to what a list, or an
arrangement, *is*.

An arrangement can be understood as a combination with a permutation
applied to it: pick which 5 cards (a combination, order-free), then
pick one of `5!` ways to arrange them. So instead of communicating
the arrangement (or `a`, the arrangement number), we can use the
combination index instead:

```python
>>> from cesets import Distinct_Combinator
>>> combinations = Distinct_Combinator(deck, 5)
>>> combinations.len()
2598960
>>> c = combinations.index(hand)
>>> c
607745

```

And since a combination is unordered, that index doesn't care what
order the same 5 cards are handed to it in either -- every one of the
`5! = 120` reorderings of `hand` produces the exact same `c`:

```python
>>> import itertools
>>> all(combinations.index(reordering) == c for reordering in itertools.permutations(hand))
True

```

This isn't just a qualitative "it's smaller" claim, it's exact: the
combination index needs precisely `log2(5!)` fewer bits than the
arrangement index does, because that's exactly the ordering
information being dropped:

```python
>>> from math import log2, factorial as fact
>>> log2(arrangements.len()) - log2(combinations.len())
6.90689059560852
>>> log2(fact(5))
6.906890595608519

```

Communicating a hand as a combination index instead of an arrangement
(or, worse, a full shuffle index) costs you exactly the bits worth of
information that was never relevant in the first place, no more, no
less.

One practical caveat: during an actual hand, updating players about
the current state of the remaining deck would need *more* information
to communicate, not less, since the space of remaining cards keeps
shrinking as cards come off the top. So a scheme like this only stays
simple if every combination number always refers back to the original
52-card setup, as if none of the cards dealt so far had been removed,
rather than being re-derived against whatever's left in the deck at
that moment.

## Counting hand shapes, mset-style

Here's where the multiset-combination machinery this project borrowed
from mset earns its keep on a genuinely famous combinatorics problem:
counting how many 5-card hands fall into each standard poker
category.

A deck is 13 ranks, 4 suits each. Instead of thinking "which 5 of 52
cards", think "how many cards of each rank" -- exactly what
`Natural_Multiset_Combinator` computes, with each of the 13 ranks
capped at a capacity of 4:

```python
>>> from cesets import Natural_Multiset_Combinator
>>> from collections import Counter
>>> from math import comb
>>> rank_shapes = Natural_Multiset_Combinator((4,) * 13, 5)
>>> rank_shapes.len()
6175

```

6,175 distinct "rank shapes" a 5-card hand can have, each one a
combination of ranks like `(0, 0, 3, 3, 7)` (two of one rank, two of
another, one of a third). What we actually want is how many *hands*,
suits included, realize each shape -- and since suits are
distinguishable, that's exactly mset's own "how many ways to realize
this count-pattern" idea: for a rank appearing `k` times in the shape,
there are `comb(4, k)` ways to pick which suits, so the realization
count for a whole shape is the product across its ranks:

```python
>>> def realization_count(shape):
...     total = 1
...     for count in Counter(shape).values():
...         total *= comb(4, count)
...     return total
...
>>> sum(realization_count(shape) for shape in rank_shapes) == comb(52, 5)
True

```

Grouping shapes by their sorted multiplicities (`(2, 1, 1, 1)` for
"one pair", `(3, 2)` for "full house", and so on) and summing the
realization counts within each group reproduces the standard 5-card
poker hand-shape frequency table exactly:

```python
>>> totals = Counter()
>>> for shape in rank_shapes:
...     pattern = tuple(sorted(Counter(shape).values(), reverse=True))
...     totals[pattern] += realization_count(shape)
...
>>> for pattern in sorted(totals):
...     print(pattern, totals[pattern])
...
(1, 1, 1, 1, 1) 1317888
(2, 1, 1, 1) 1098240
(2, 2, 1) 123552
(3, 1, 1) 54912
(3, 2) 3744
(4, 1) 624

```

`(2, 1, 1, 1)` is one pair (1,098,240 hands), `(2, 2, 1)` is two pair,
`(3, 1, 1)` is three of a kind, `(3, 2)` is a full house, and `(4, 1)`
is four of a kind -- all exact, all obtained without enumerating a
single one of the 2,598,960 hands directly.

Worth being upfront about the one thing this doesn't give you for
free: `(1, 1, 1, 1, 1)`, five different ranks, is *not* "high card" on
its own. It still contains every straight, flush, straight flush, and
royal flush, since a rank shape has no idea whether those five ranks
happen to be consecutive, or whether all five cards happen to share a
suit. Pulling those out needs a genuinely different check (rank
adjacency, and suit agreement) that the capped-multiset abstraction
this project builds on doesn't model at all -- a real, honest
boundary of what "choose from capped classes" can tell you, not a bug
to route around.

## Multiple decks: where the multiset machinery stops being optional

Casinos routinely shuffle several decks together for other games
(a 6-deck blackjack shoe, say); nothing stops the same setup from
being used for poker, and it makes for a much better showcase of this
project's multiset capabilities than a single deck does. Shuffle `d`
decks together and each of the 52 card types now has multiplicity
`d`, a genuine multiset, not a set -- exactly `Natural_Multiset_Permutator`/
`Natural_Multiset_Combinator`'s territory, and no longer something
`d!`/`comb(n, k)` alone can answer.

The permutation count is `(52*d)! / (d!)**52`, computed here via the
same `Natural_Multiset_Permutator` used throughout this project rather
than the formula directly, formatted with the library's own
`format_funct` (the same truncation `repr` uses) since these get big
fast:

```python
>>> from cesets import Natural_Multiset_Permutator
>>> nmp = Natural_Multiset_Permutator((1,) * 52)
>>> for decks in range(1, 7):
...     count = Natural_Multiset_Permutator((decks,) * 52).len()
...     print(decks, nmp.format_funct(count))
...
1 8.0658...00000e+67
2 2.2868...00000e+150
3 2.5675...00000e+235
4 4.0853...00000e+321
5 2.9227...00000e+408
6 5.5124...00000e+495

```

More interesting is what happens to 5-card hands. The naive way to
count "combinations with repetition allowed" is stars and bars,
`comb(k + m - 1, k)` for choosing `k` from `m` types with *unlimited*
repeats -- and it's a trap here, because repeats aren't unlimited,
they're capped at `d` copies per card. Comparing it against the
correct, capacity-respecting count from `Natural_Multiset_Combinator`
for each deck count:

```python
>>> stars_and_bars = comb(5 + 52 - 1, 5)
>>> stars_and_bars
3819816
>>> for decks in range(1, 7):
...     hands = Natural_Multiset_Combinator((decks,) * 52, 5).len()
...     print(decks, hands, hands == stars_and_bars)
...
1 2598960 False
2 3748160 False
3 3817112 False
4 3819764 False
5 3819816 True
6 3819816 True

```

Stars and bars overcounts for 1 through 4 decks (sometimes badly --
for a single deck it's off by nearly 50%), because it's perfectly
happy counting hands with 5 copies of the same card, which don't
exist yet when there are only 1-4 of that card in play. It only
becomes correct at 5 and 6 decks, and for a very precise reason: it
stops mattering that repeats are capped once the cap (`d`) is at
least as large as the hand size (`k = 5`), which is exactly the
"capacities can't bind" shortcut `multiset_combination_count` itself
uses internally, worked through in
[COMBINATORICS.md](COMBINATORICS.md). Below 5 decks, the cap is the
whole story; stars and bars simply doesn't know it exists.

## For scale

`52!`, the size of the shuffle space this whole example started from,
is:

```python
>>> factorial(52)
80658175170943878571660636856403766975289505440883277824000000000000

```

Roughly `8.07 * 10**67`. For scale: that's comfortably past the
estimated number of atoms making up the entire planet Earth (commonly
put at around `10**50`), though still well short of the estimated
number of atoms in the observable universe (commonly put at around
`10**80`). Somewhere in between those two very rough estimates is
where a proper shuffle lives -- which is the usual, and reasonably
accurate, basis for the claim that a well-shuffled deck is an
arrangement that has, in all likelihood, never existed before.

That comparison stops being interesting once multiple decks enter the
picture. The 6-deck shuffle count from the table above has 496 digits:

```python
>>> perms_6_decks = Natural_Multiset_Permutator((6,) * 52).len()
>>> len(str(perms_6_decks))
496
>>> perms_6_decks > 10**80
True
>>> perms_6_decks > (10**80)**6
True

```

Not just past one estimated universe's worth of atoms, but past that
same rough estimate raised to the 6th power -- purely an illustrative
calculation, not a physical claim, but a proper measure of how far
"multiply the deck count by 6" actually moves the number: from
comfortably-sized to nothing left in reality to meaningfully compare
it against.
