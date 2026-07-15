# A shop's database: sets, arrangements, and combinations

A small shop, a fixed inventory, and a day's worth of purchases --
this is the worked example the "purchase transaction" discussion from
this project's own history kept getting mentioned without ever
actually being written down. It's the same idea POKER.md builds a
hand around (order-free multiset counting, `Natural_Multiset_Combinator`,
`Natural_Multiset_Arranger`), applied to a database problem instead of
a card game: given a log of purchases, how should closing time
compress it onto disk?

## The shop

Twelve products, each with a stock cap and a price:

```python
>>> from collections import namedtuple, Counter
>>> Product = namedtuple('Product', ['name', 'stock', 'price'])
>>> inventory = [
...     Product('apple', 40, 0.50),
...     Product('banana', 35, 0.30),
...     Product('bread', 20, 2.50),
...     Product('milk', 25, 1.80),
...     Product('eggs', 30, 3.20),
...     Product('coffee', 15, 6.50),
...     Product('tea', 15, 4.00),
...     Product('cheese', 18, 5.50),
...     Product('butter', 20, 3.00),
...     Product('rice', 22, 2.20),
...     Product('pasta', 22, 1.60),
...     Product('chocolate', 25, 2.80),
... ]
>>> capacities = tuple(p.stock for p in inventory)
>>> prices = tuple(p.price for p in inventory)
>>> n = len(inventory)
>>> n
12

```

Each purchase is stored as a tuple of product indices, in the order
they were rung up at the register -- indices into `inventory`, not
names, the same way `Natural_Multiset_Combinator`/`Natural_Multiset_Arranger`
address classes by canonical label `0..n-1` rather than by object
identity. A customer buying one item is a length-1 tuple; a customer
buying several, some repeated, is a longer one with duplicate labels:

```python
>>> import random
>>> random.seed(2026)
>>> shop_db = []
>>> for _ in range(24):
...     size = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 25, 20, 12, 8, 5])[0]
...     shop_db.append(tuple(random.choices(range(n), k=size)))
...
>>> len(shop_db)
24
>>> shop_db[:6]
[(6,), (10, 1), (7,), (9, 6, 8), (9, 7, 2, 7), (9,)]
>>> sizes = Counter(len(p) for p in shop_db)
>>> dict(sorted(sizes.items()))
{1: 5, 2: 9, 3: 6, 4: 2, 5: 2}

```

Purchase index 4, `(9, 7, 2, 7)`, is rice, cheese, bread, and a second
cheese -- exactly the "buys more, including repeats" case:

```python
>>> [inventory[i].name for i in shop_db[4]]
['rice', 'cheese', 'bread', 'cheese']

```

This whole file, up to the closing-time operation, is `shop_db`: a
plain Python list, one tuple per transaction, nothing compressed yet.

## The tempting shortcut: just make it a set

The instinct at closing time is the same one this project's own
history already worked through for a poker hand: the register doesn't
care what order items were scanned in, only what was sold. So why not
store each purchase as a `set`?

```python
>>> set_db = [set(p) for p in shop_db]

```

This is wrong, and it's worth being precise about *how* it's wrong
rather than waving at it. A `set` collapses duplicates -- so a
purchase of two cheeses and a purchase of one cheese, once the rest of
the basket matches, become indistinguishable:

```python
>>> shop_db[4]
(9, 7, 2, 7)
>>> set_db[4]
{9, 2, 7}
>>> len(shop_db[4]), len(set_db[4])
(4, 3)

```

The repeat is simply gone. Not approximated, not compressed -- gone,
with no way to tell from `set_db[4]` alone whether the customer bought
one cheese or ten. Across this run:

```python
>>> lossy = [p for p in shop_db if len(set(p)) != len(p)]
>>> len(lossy)
2

```

Two purchases out of 24 already lost real information. Since prices
are attached to products, this isn't an abstract complaint -- it
directly understates revenue if `set_db` is ever treated as a source
of truth:

```python
>>> true_revenue = sum(prices[i] for p in shop_db for i in p)
>>> set_revenue = sum(sum(prices[i] for i in s) for s in set_db)
>>> round(true_revenue, 2)
194.4
>>> round(set_revenue, 2)
179.6
>>> round(true_revenue - set_revenue, 2)
14.8

```

$14.80 of real sales, silently missing, because two customers bought a
second unit of something already in their basket.

## Doing it correctly: arrangements and combinations

`shop_db`'s own order (checkout scan order) is exactly the "order
that's real but nobody needs to keep" case this project has run into
before -- so this is `Natural_Multiset_Arranger`'s and
`Natural_Multiset_Combinator`'s territory directly, addressed against
the shop's own `capacities`, not the depleting stock at the moment of
each sale (the same simplifying choice POKER.md's own multi-deck
section makes explicit: every index refers back to the *original*
setup, so it stays meaningful without having to know what happened in
between).

Purchases vary in size -- one item for some customers, six for others
-- so an index alone isn't enough to place a purchase back into the
right space; it needs its size alongside it:

```python
>>> from esets import Natural_Multiset_Arranger, Natural_Multiset_Combinator
>>> arrangers = {}
>>> combinators = {}
>>> def get_arranger(k):
...     if k not in arrangers:
...         arrangers[k] = Natural_Multiset_Arranger(capacities, k)
...     return arrangers[k]
...
>>> def get_combinator(k):
...     if k not in combinators:
...         combinators[k] = Natural_Multiset_Combinator(capacities, k)
...     return combinators[k]
...
>>> arrange_db = [(len(p), get_arranger(len(p)).index(p)) for p in shop_db]
>>> comb_db = [(len(p), get_combinator(len(p)).index(tuple(sorted(p)))) for p in shop_db]

```

`Natural_Multiset_Arranger` preserves order, so it takes the purchase
exactly as scanned. `Natural_Multiset_Combinator` doesn't, and its
`.index()` needs the purchase in canonical (sorted) order to find it --
passing it unsorted raises `ValueError`, since a combination has no
notion of "the second element" to match against.

Both reconstruct exactly, unlike `set_db`:

```python
>>> all(get_arranger(k)[idx] == p for p, (k, idx) in zip(shop_db, arrange_db))
True
>>> all(get_combinator(k)[idx] == tuple(sorted(p)) for p, (k, idx) in zip(shop_db, comb_db))
True

```

`arrange_db` reconstructs the purchase itself, scan order included.
`comb_db` reconstructs the *sorted* purchase -- everything the shop
actually needs (which items, how many of each) with the one detail it
never needed (scan order) gone by construction rather than by
accident. Revenue reconstructs exactly from either:

```python
>>> comb_revenue = sum(
...     sum(prices[i] for i in get_combinator(k)[idx]) for k, idx in comb_db
... )
>>> round(comb_revenue, 2) == round(true_revenue, 2)
True
>>> arrange_revenue = sum(
...     sum(prices[i] for i in get_arranger(k)[idx]) for k, idx in arrange_db
... )
>>> round(arrange_revenue, 2) == round(true_revenue, 2)
True

```

## Measuring it, not assuming it

`sys.getsizeof` alone understates a `list` of `tuple`s or `set`s -- it
only counts the list's own overhead, not what it points to. A small
recursive helper, careful not to double-count anything already seen
by reference, gives the real total:

```python
>>> import sys
>>> def deep_size(obj, seen=None):
...     if seen is None:
...         seen = set()
...     oid = id(obj)
...     if oid in seen:
...         return 0
...     seen.add(oid)
...     size = sys.getsizeof(obj)
...     if isinstance(obj, (list, tuple, set, frozenset)):
...         for item in obj:
...             size += deep_size(item, seen)
...     return size
...
>>> deep_size(shop_db)
2208
>>> deep_size(set_db)
6280
>>> deep_size(arrange_db)
2540
>>> deep_size(comb_db)
2512

```

`set_db` isn't a close second here -- it's the largest of the four,
by a wide margin, despite holding *less* information than any of the
others. A `set`'s hash table (sized to keep its load factor low, and
rounded up to a power of two) costs far more overhead than a `tuple`
ever does for a handful of elements. `set_db` loses on both axes at
once: it's wrong, and it's not even small.

`arrange_db` and `comb_db`, on the other hand, are barely
distinguishable from `shop_db` in raw bytes here -- and `comb_db`
isn't even the smallest of the three. That's not a mistake in the
comparison; it's CPython's small-integer cache (`-5` to `256`) doing
exactly what it does everywhere else. Every product index in this
12-item inventory is a cached, shared integer that costs nothing extra
to reference again -- `shop_db`'s tuples are close to free. The
combinatorial *index* stored in `arrange_db`/`comb_db`, meanwhile, is
one specific, usually large, integer per purchase -- not cached, and
paid for in full. Comparing raw Python object bytes at this scale
mostly measures an implementation detail of CPython's integer
allocator, not the actual information content of any of these
representations.

## The comparison that isn't a CPython artifact

Scaling up removes the small-integer cache as a confound and exposes
the difference `sys.getsizeof` was hiding. A words-only synthetic
catalog, no product names needed for this part, since the raw index
values are the whole point:

```python
>>> random.seed(5)
>>> n2 = 80
>>> caps2 = tuple(random.randint(15, 60) for _ in range(n2))
>>> shop_db2 = []
>>> for _ in range(200):
...     size = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 25, 20, 12, 8, 5])[0]
...     shop_db2.append(tuple(random.choices(range(n2), k=size)))
...
>>> arrangers2, combinators2 = {}, {}
>>> def A2(k):
...     if k not in arrangers2:
...         arrangers2[k] = Natural_Multiset_Arranger(caps2, k)
...     return arrangers2[k]
...
>>> def C2(k):
...     if k not in combinators2:
...         combinators2[k] = Natural_Multiset_Combinator(caps2, k)
...     return combinators2[k]
...
>>> arrange_db2 = [(len(p), A2(len(p)).index(p)) for p in shop_db2]
>>> comb_db2 = [(len(p), C2(len(p)).index(tuple(sorted(p)))) for p in shop_db2]
>>> deep_size(shop_db2)
17792
>>> deep_size(arrange_db2)
19844
>>> deep_size(comb_db2)
19748

```

Raw bytes still favor `shop_db2` -- every one of its product indices
(`0` to `79`) is still inside the cached range, so this isn't the
comparison that settles anything either. The one that does is bit
length: how many bits does each index actually need, independent of
whatever any particular Python build happens to cache?

```python
>>> arrange_bits = sum(idx.bit_length() for k, idx in arrange_db2)
>>> comb_bits = sum(idx.bit_length() for k, idx in comb_db2)
>>> arrange_bits
3200
>>> comb_bits
2701
>>> arrange_bits - comb_bits
499

```

499 bits saved across 200 purchases just by not paying for scan order
-- the exact `POKER.md`/`INCLUSIONEXCLUSION.md` idea (`log2(k!)`-ish
savings per purchase, this time summed over an actual batch) rather
than a single hand. `comb_db2`'s indices are provably smaller than
`arrange_db2`'s for the same purchases, for the same reason a
combination space is always smaller than the arrangement space it's
carved out of: this is the one comparison in this file that isn't an
artifact of how CPython happens to store small integers.

## What actually drives the crossover: basket size, not catalog size

Growing the catalog alone didn't get `arrange_db`/`comb_db` ahead of
`shop_db` -- `n2 = 80` above already shows that; every product index
still fit the cached range, and neither compressed form pulled ahead.
The real lever is basket size, and it's structural, not a caching
effect at all: `shop_db`'s tuple needs one pointer slot for *every
item in the purchase*, so its cost is `O(basket size)` regardless of
whether the referenced integers are cached. `arrange_db`/`comb_db` is
always a 2-tuple -- `(size, index)` -- no matter how many items were
bought; only the single index integer grows. Holding catalog size and
capacity fixed and growing only the basket size isolates this
cleanly:

```python
>>> n3 = 30
>>> for basket_size in [6, 10, 14, 18]:
...     random.seed(9)
...     caps3 = (basket_size + 10,) * n3
...     shop_db3 = [tuple(random.choices(range(n3), k=basket_size)) for _ in range(100)]
...     A3 = Natural_Multiset_Arranger(caps3, basket_size)
...     C3 = Natural_Multiset_Combinator(caps3, basket_size)
...     arrange_db3 = [(basket_size, A3.index(p)) for p in shop_db3]
...     comb_db3 = [(basket_size, C3.index(tuple(sorted(p)))) for p in shop_db3]
...     print(basket_size, deep_size(shop_db3), deep_size(arrange_db3), deep_size(comb_db3))
...
6 11360 10148 10148
10 14560 10548 10148
14 17760 10948 10548
18 20960 10948 10548

```

`shop_db3` grows in a straight line with basket size; `arrange_db3`
and `comb_db3` barely move. The crossover already happened by
`basket_size = 6` in this setup, and by `18` `shop_db3` is roughly
twice the size of either compressed form -- with no CPython caching
quirk involved anywhere in this explanation. `comb_db3` stays at or
below `arrange_db3` throughout, the same order-independence edge as
above, holding at every basket size tested.

## One honest boundary

This file's `n = 80` and `n = 30` synthetic catalogs above are
deliberate choices, not just "big enough to see the effect and no
more thought given to it." An earlier draft of this section claimed
ranking hits "the same wall" `COMBINATORICS.md` and
`INCLUSIONEXCLUSION.md` document for plain counting -- roughly
250-300 classes -- and that turned out to be too simple. Reading
`get_multiset_combination_number` and `get_multiset_arrangement_number`
directly ([esets/ecombinatorics.py:301](esets/ecombinatorics.py) and
[esets/ecombinatorics.py:521](esets/ecombinatorics.py)) shows why:
counting's shortcuts -- the closed forms this project added while
benchmarking against inclusion-exclusion -- all live inside
`multiset_combination_count` itself. Ranking calls that function for
a block size at each step, but its own search -- the part that walks
toward an answer -- has no equivalent shortcut. `get_multiset_combination_number`'s
`locate` searches for the right count within the *current* class one
unit at a time before moving to the next class, so its depth is
closer to `classes x min(capacity, basket size)` than to `classes`
alone. `get_multiset_arrangement_number`'s `locate` searches through
*candidate classes* once per item in the purchase, closer to `classes
x basket size`. Both are worse than "class count alone," and neither
gives a single fixed safe boundary -- it's why a large catalog with
small, tight purchases can survive fine while a much smaller catalog
with a handful of large purchases can't. Verified directly: `n = 300`
with capacity `3` and a basket of `3` completes without incident,
while `n = 80` with a basket of `50` raises `RecursionError` well
before reaching it. A real shop with either a genuinely large catalog
*or* customers who buy dozens of items in one purchase would need
this fixed the same way the counting side eventually was -- not
attempted here, since ranking is a different recursion with a
different shape, not a corollary of the counting fixes.
