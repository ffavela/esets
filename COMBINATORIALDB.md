# A shop's database: sets, arrangements, and combinations

A small shop, a fixed inventory, and a day's worth of purchases. It's
the same idea POKER.md builds a hand around (order-free multiset
counting, `Natural_Multiset_Combinator`, `Natural_Multiset_Arranger`),
applied to a database problem instead of a card game: given a log of
purchases, how should closing time compress it onto disk?

*(This file went through a round of revision after its first
publication corrected an inaccurate claim about where ranking's
recursion limit actually comes from; see "One honest boundary" below
for the corrected version.)*

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
>>> shop_size = deep_size(shop_db)
>>> set_size = deep_size(set_db)
>>> arrange_size = deep_size(arrange_db)
>>> comb_size = deep_size(comb_db)
>>> set_size > shop_size
True
>>> comb_size <= arrange_size
True

```

`set_db` isn't a close second here -- it's the largest of the four,
by a wide margin, despite holding *less* information than any of the
others. Exact byte counts are CPython-version-specific (`sys.getsizeof`
reflects internal object layout that changes across versions, which is
why only the *ordering* checked above is asserted, not these numbers
directly), but for scale, measured once on this machine:

| representation | bytes |
|-----------------|------:|
| `shop_db`       |  2208 |
| `set_db`        |  6280 |
| `arrange_db`    |  2540 |
| `comb_db`       |  2512 |

A `set`'s hash table (sized to keep its load factor low, and rounded
up to a power of two) costs far more overhead than a `tuple` ever does
for a handful of elements. `set_db` loses on both axes at once: it's
wrong, and it's not even small.

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
>>> shop2_size = deep_size(shop_db2)
>>> arrange2_size = deep_size(arrange_db2)
>>> comb2_size = deep_size(comb_db2)
>>> shop2_size < arrange2_size and shop2_size < comb2_size
True
>>> comb2_size <= arrange2_size
True

```

Raw bytes still favor `shop_db2` here -- again, exact counts are
version-specific, only the ordering above is asserted, but for scale,
measured once on this machine:

| representation | bytes |
|-----------------|------:|
| `shop_db2`      | 17792 |
| `arrange_db2`   | 19844 |
| `comb_db2`      | 19748 |

Every one of its product indices (`0` to `79`) is still inside the
cached range, so this isn't the comparison that settles anything
either. The one that does is bit length: how many bits does each
index actually need, independent of whatever any particular Python
build happens to cache?

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
>>> results = []
>>> for basket_size in [6, 10, 14, 18]:
...     random.seed(9)
...     caps3 = (basket_size + 10,) * n3
...     shop_db3 = [tuple(random.choices(range(n3), k=basket_size)) for _ in range(100)]
...     A3 = Natural_Multiset_Arranger(caps3, basket_size)
...     C3 = Natural_Multiset_Combinator(caps3, basket_size)
...     arrange_db3 = [(basket_size, A3.index(p)) for p in shop_db3]
...     comb_db3 = [(basket_size, C3.index(tuple(sorted(p)))) for p in shop_db3]
...     results.append(
...         (basket_size, deep_size(shop_db3), deep_size(arrange_db3), deep_size(comb_db3))
...     )
...
>>> all(comb <= arrange for _, _, arrange, comb in results)
True
>>> results[0][1] > results[0][3]
True
>>> (results[-1][1] - results[0][1]) > (results[-1][3] - results[0][3])
True

```

`shop_db3` grows in a straight line with basket size; `arrange_db3`
and `comb_db3` barely move. Again, only the ordering checked above is
asserted, not these exact counts, but for scale, measured once on this
machine:

| basket_size | `shop_db3` | `arrange_db3` | `comb_db3` |
|------------:|-----------:|--------------:|-----------:|
|           6 |      11360 |          10148 |      10148 |
|          10 |      14560 |          10548 |      10148 |
|          14 |      17760 |          10948 |      10548 |
|          18 |      20960 |          10948 |      10548 |

The crossover already happened by `basket_size = 6` in this setup
(`results[0][1] > results[0][3]` above), and by `18` `shop_db3` is
roughly twice the size of either compressed form, with no CPython
caching quirk involved anywhere in this explanation. `comb_db3` stays
at or below `arrange_db3` throughout, the same order-independence edge
as above, holding at every basket size tested.

## One honest boundary

This file's `n = 80` and `n = 30` synthetic catalogs above are
deliberate choices, not just "big enough to see the effect." Ranking
-- what `.index()` is doing throughout this file -- does *not* hit the
same wall `COMBINATORICS.md` and `INCLUSIONEXCLUSION.md` document for
plain counting (roughly 250-300 classes); it's more fragile than
that. Reading `get_multiset_combination_number` and
`get_multiset_arrangement_number` directly
([esets/ecombinatorics.py:301](esets/ecombinatorics.py) and
[esets/ecombinatorics.py:521](esets/ecombinatorics.py)) shows why:
counting's shortcuts -- the closed forms inside
`multiset_combination_count` itself -- don't apply to ranking.
Ranking calls that function for a block size at each step, but its
own search -- the part that walks toward an answer -- has no
equivalent shortcut. `get_multiset_combination_number`'s
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

## Letting the inventory actually deplete

Everything above addresses `arrange_db`/`comb_db` against the shop's
*original* `capacities`, never against whatever stock is actually left
at the moment of a given sale -- a choice this file made by analogy
with `POKER.md`'s own multi-deck section, which does the same thing
for a different, stated reason: re-deriving a hand's number against a
shrinking deck needs *more* information to communicate it, not less,
since the number alone stops being self-sufficient without also
knowing the deck's current shape. `POKER.md` never mentions card
counting -- that's a real, separate concern in a multi-party game
(transmitting deck state right after dealing to one player could let
everyone else infer that player's hand), but it isn't the reason given
there, and it doesn't transfer here anyway: a shop's own database has
no other players to keep in the dark.

What *does* transfer is worth checking on its own terms rather than
assumed. Unlike a single poker hand communicated in isolation,
`arrange_db`/`comb_db` are already a full log, meant to be replayed
start to finish -- so the "extra information" `POKER.md` warns about
isn't extra at all here, it's just the running stock level, which
falls out for free from replaying the log in order. The real cost is
different: today, every entry in `arrange_db`/`comb_db` decodes
independently, in any order, in parallel (the round-trip check earlier
in this file does exactly that with a single `all(...)` over
`zip(shop_db, arrange_db)`). Depleting stock breaks that outright --
decoding purchase 17 needs purchases 0 through 16 already replayed, to
know what stock was actually left. That's a real, structural trade,
not a footnote.

There's a harder wall underneath it, too. Once an item sells out
completely, its capacity hits zero, and the constructors reject that
outright:

```python
>>> Natural_Multiset_Arranger((3, 0, 2), 2)
Traceback (most recent call last):
    ...
ValueError: Multiplicities must be positive integers

```

So depleting stock for real means dropping sold-out items from the
alphabet entirely once they run out, not just letting their capacity
reach zero -- a small compacting layer between the shop's product
indices and the canonical labels `Natural_Multiset_Arranger` actually
sees:

```python
>>> def get_depleting_arranger(remaining_stock, k):
...     active_items = [i for i, c in enumerate(remaining_stock) if c > 0]
...     caps = tuple(remaining_stock[i] for i in active_items)
...     return Natural_Multiset_Arranger(caps, k), active_items
...

```

`active_items[compact_label]` is the original product index a
compacted label stands for at that point in the log -- built fresh
each time from whatever's still in stock, so a product that sold out
three purchases ago simply isn't a candidate class any more.

Running this against `shop_db`, the very same 24-purchase log used
throughout this file, round-trips correctly, replaying stock as it
goes:

```python
>>> remaining = list(capacities)
>>> deplete_db = []
>>> for p in shop_db:
...     A, active_items = get_depleting_arranger(remaining, len(p))
...     pos = {orig: compact for compact, orig in enumerate(active_items)}
...     compact_p = tuple(pos[i] for i in p)
...     deplete_db.append((len(p), A.index(compact_p)))
...     for c in p:
...         remaining[c] -= 1
...
>>> remaining_check = list(capacities)
>>> reconstructed = []
>>> for (k, idx), p in zip(deplete_db, shop_db):
...     A, active_items = get_depleting_arranger(remaining_check, k)
...     reconstructed.append(tuple(active_items[c] for c in A[idx]))
...     for c in p:
...         remaining_check[c] -= 1
...
>>> reconstructed == shop_db
True

```

Now the number this section actually exists to check: are the indices
smaller? Against this file's own moderate-sized inventory (12 products,
capacity 15-40 each) and a 24-purchase log that never drives anything
close to sold out:

```python
>>> [idx for _, idx in deplete_db] == [idx for _, idx in arrange_db]
True
>>> min(remaining)
6

```

Identical, purchase for purchase -- not approximately, exactly. That's
surprising given the premise, and worth explaining rather than
shrugging off: the ranking recursion's own "capacities can't bind"
shortcut ([esets/ecombinatorics.py:458](esets/ecombinatorics.py))
fires whenever remaining capacity for every class involved stays at or
above the purchase size, and it computes the *same* answer either way
once it fires -- depleted stock only starts changing an index once
some class's remaining capacity drops close to a purchase's own size,
not just because stock ticked down. `min(remaining) == 6` here, comfortably
above every basket size in this log (`COMBINATORIALDB.md`'s own `sizes`
table earlier tops out at `6`), so the shortcut fires identically
throughout and depleting stock bought nothing on this particular day.

## Making the effect actually show up

Getting depletion to matter means picking a shop shape where it
plausibly *does* bind -- a small inventory, relative to basket size,
worked all the way down toward empty:

```python
>>> random.seed(42)
>>> n5 = 5
>>> deplete_capacities = tuple(random.randint(8, 14) for _ in range(n5))
>>> deplete_capacities
(13, 8, 8, 13, 10)
>>> sum(deplete_capacities)
52

```

Generating the purchase log itself has to change too: sampling
uniformly from all `n5` products the way `shop_db`/`shop_db2` do would
mostly just fail once stock ran low, rather than modeling a shop that
naturally stops selling what it doesn't have. So each purchase draws
only from products still in stock:

```python
>>> random.seed(99)
>>> remaining_gen = list(deplete_capacities)
>>> deplete_log = []
>>> while len(deplete_log) < 60:
...     available = [i for i, c in enumerate(remaining_gen) if c > 0]
...     if not available:
...         break
...     size = min(random.randint(2, 4), len(available))
...     basket, pool = [], list(available)
...     for _ in range(size):
...         if not pool:
...             break
...         choice = random.choice(pool)
...         basket.append(choice)
...         remaining_gen[choice] -= 1
...         if remaining_gen[choice] == 0:
...             pool.remove(choice)
...     deplete_log.append(tuple(basket))
...
>>> len(deplete_log)
21
>>> all(c == 0 for c in remaining_gen)
True

```

Sold out completely, all 5 products, after 21 purchases. Ranking every
purchase both ways -- against the fixed original capacities, and
against genuinely depleting, alphabet-shrinking stock:

```python
>>> fixed5 = {}
>>> def FA5(k):
...     if k not in fixed5:
...         fixed5[k] = Natural_Multiset_Arranger(deplete_capacities, k)
...     return fixed5[k]
...
>>> fixed_bits = [FA5(len(p)).index(p).bit_length() for p in deplete_log]
>>> remaining5 = list(deplete_capacities)
>>> dep_bits, active_counts = [], []
>>> for p in deplete_log:
...     A, active_items = get_depleting_arranger(remaining5, len(p))
...     pos = {orig: compact for compact, orig in enumerate(active_items)}
...     compact_p = tuple(pos[i] for i in p)
...     dep_bits.append(A.index(compact_p).bit_length())
...     active_counts.append(len(active_items))
...     for c in p:
...         remaining5[c] -= 1
...
>>> q = len(fixed_bits) // 4
>>> sum(fixed_bits[:q]) / q, sum(dep_bits[:q]) / q
(6.0, 6.0)
>>> sum(fixed_bits[-q:]) / q, sum(dep_bits[-q:]) / q
(1.2, 0.6)
>>> sum(fixed_bits), sum(dep_bits)
(99, 91)

```

The same shape as before, right up until it isn't: the first quarter
of this log matches exactly (`6.0` either way), for the identical
reason the full `shop_db` run above matched throughout -- stock is
still comfortably above basket size early on. The last quarter is
where it breaks open, average bits per purchase roughly halving
(`1.2` down to `0.6`), because the number of *active classes* itself
collapses as products sell out:

```python
>>> active_counts[-8:]
[5, 4, 3, 3, 3, 2, 1, 1]
>>> fixed_bits[-8:]
[4, 4, 5, 0, 2, 4, 0, 0]
>>> dep_bits[-8:]
[4, 3, 3, 0, 1, 2, 0, 0]

```

By the last two purchases only one product is left at all -- there's
exactly one possible arrangement remaining, so the index needs `0`
bits to communicate it, while the fixed scheme keeps paying for
arrangement space against products that no longer exist to be sold.
Total across this run: `99` bits fixed versus `91` depleting -- a
modest number that undersells what's actually happening, since almost
all of the saving is concentrated in the handful of purchases nearest
the stockout, not spread evenly across the log.

Put together honestly: depleting stock isn't a free improvement over
this file's original choice. On a normal day, with stock well above
basket size throughout, it changes nothing at all, while giving up
independent, parallel decodability for a purely sequential replay. It
only earns its keep once a shop's inventory genuinely runs thin --
closeout sales, near-stockout windows, a small catalog worked hard --
and there, the effect isn't gradual, it's a sharp collapse right at
the end, down to zero bits at the moment there's nothing left to
choose from at all.
