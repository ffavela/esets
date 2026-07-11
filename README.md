# esets

The datastructure that nobody asked for is finally here. (beta)

## What is it? (An informal introduction)

**esets** stands for enumerated sets. They can handle arbitrarily
  large sets, and even represent infinite numerable sets (like the set
  of even numbers). This is possible since in essence they are lazy
  generated sequences.

In a sense, this could be described like a memoryless data structure,
an obvious misnomer (but not for an obvious reason).  Something where
the structure is in memory but not the data. The data is directly
generated from the structure as soon as it is needed so there is no
need to store the entirety of the data on memory. Despite this you may
access the data via indexing, and operations such as slicing are
accessible. Note that most eset implementations are random access see
[BEset, Eset, and EMap: what's actually underneath](#beset-eset-and-emap-whats-actually-underneath)
for details.

### Python already has sets, why create another implementation?

A python set is an unordered collection of unique elements. They
support common set operations such as union and intersection and can
be counted (supports `len`). An `eset` doesn't support the common set
operations, it does support `len` (see further for caveats) and
despite ordering being normally ignored here it plays a central
role. This `set` implementation (`eset`) sacrifices all those common
`set` operations in favor of enumeration. This unlocks slicing on them
and the capability of defining in a computer extremely large or even
infinite sets, more properly infinite `esets`.

### But don't indices relate to locations in memory for sequences?

For the most part yes, the same way as in dictionaries the keys also
relate to locations in memory. But at the end of the day a
mathematical operation is performed to get the memory address and then
the values are fetched from memory. For `esets` the mathematical
operation gives directly the answer. You may imagine it as fetching
the data from a meta memory space, or in a more honest sense from a
fake memory space.

In a bit more technical sense, [eset.py](eset.py) is and abstract base
class (ABC) and [esets.py](esets.py) has a set of classes that derive
from the ABC, they implement the required methods like the function
that gets the value given an index and the corresponding inverse
function.

### Why?

Well it turns out it is easier to define the whole rather than a part
of it, and the whole can be quite large. It kind of sounds paradoxical
but perhaps this (probably apocryphal) quote from Michelangelo may
help.  When asked about his difficult process during the sculpting of
David he responded:

> It is easy. You just chip away the stone that doesn’t look like
> David.

This is of course a sarcastic response, chipping away stuff is were
the difficulty is. Anydoby can describe a block of marble no matter
the size, it is a humbling experience that someone had the talent,
determination and character to pull that off and turn that marble
block into David.

To put it into the `eset` perspective, mathematically it is easier to
describe and enumerate the entire infinite set of Whole numbers than
the chipped away subset of twin prime numbers or the odd perfect
numbers, even if this later one may actually turn out to be finite or
even empty.

Note also that it is easier to describe the evens than to describe the
set of even numbers up to some humongous value. Because that humongous
value can take a lot of memory while simply saying no last value
exists (infinite) can take very little.

### Is this like an is_even library?

Sure it can be used like that:

```python
>>> from esets import Evens
>>> 2 in Evens()
True
>>> 1 in Evens()
False
>>>
```

Which is cooler than testing if a value `n` is even via `n%2 == 0`.

### I'm wasting my time reading this, aren't I?

Likely, but if you can spare a bit of time please read on. As you may
start to foresee it is a bit more than an is_even library. Let's first
assign `Evens()` to a variable and check out what is in there:

```python
>>> e = Evens()
>>> e
<esets.Evens (0, 2, 4, 6, ...)>
>>>
```

Here the ellipsis (`...`) at the end means that the sequence goes on
forever. Any positive integer is there, as long as in can be stored in
memory we can check it e.g.:

```python
>>> a=4732868736587936587436587346587356843765438756438756823764823746238764283764237846238746238746237842378672385687235623746238764238746873246
>>> a in e
True
>>> a+1 in e
False
>>>
```

### So what about it's len?

About that:

```python
>>> len(e)
Traceback (most recent call last):
...
ValueError: Aleph_0 infinite
>>>
```

### This is obviously wrong, we don't have an infinite amount of memory to store the entire set!!

Correct, we aren't. It is a lazy evaluated sequence, and discrete math
is behind this.

In the spirit of Georg Cantor's work (and Leopold Kronecker of course)
we are simply establishing a relationship between the Even numbers and
the Whole numbers (0, 1, 2, ...) where the later serve as our indices.

```python
>>> for i in range(5):
...     print(i, e[i])
...
0 0
1 2
2 4
3 6
4 8
>>>
```

In fact the following is also valid:

```python
>>> for i,v in enumerate(e[:5]):
...     print(i, v)
...
0 0
1 2
2 4
3 6
4 8
>>>
```

### The relationship is clear for any index value just double it to get the respective Evens value right?

So far yes, this will not generally be the case. Similarly for the reverse
we can use dividing by two:

```python
>>> e.index(42)
21
>>>
```

### So it is just a convoluted way of doing some trivial math?

At first glance yes. But kindly note that even for this trivial
example some non-trivial operations are happening behind the
hood. Check out the following:

```python
>>> e[:10**10:3][::-5]
<esets.Evens* (19999999998, 19999999968, 19999999938, 19999999908, ..., 108, 78, 48, 18)>
>>> for i, v in enumerate(e[:10**10:3][::-5][:4]):
...     print(i, v)
...
0 19999999998
1 19999999968
2 19999999938
3 19999999908
>>>
```

It behaves just like if there was some list (an inmutable one) that
has all the elements and "complex" slices are performed on it. So not
it is not just divide by two to get the index. There is some fancy
math footwork performed behind the scenes by the **eset** to acchieve
this.

Note the `*` in `esets.Evens*`, that implies that there was a slice in
place.

Let's be a bit more ambitious say a slice using a googol (`10**100`)
on the Evens **eset**:

```python
>>> e[3:10**100]
<esets.Evens* (6, 8, 10, 12, ..., 1.9999...99992e+100, 1.9999...99994e+100, 1.9999...99996e+100, 1.9999...99998e+100)>
>>>
```

Note that when using a repr if the elements are integers and above a
certain threshold of size (like 15 chars but don't quote me on that
cause it may change), then a special notation is involved using a
decimal point a an ellipsis, the very last digits of the decimal
expansion and the multiplicative power of ten factor.


So naturally here:

```python
>>> 4 in e[3:10**100]
False
>>> 6 in e[3:10**100]
True
>>> 10**6 in e[3:10**100]
True
>>> 10**100 in e[3:10**100]
True
>>> 2*10**100-2 in e[3:10**100]
True
>>> 2*10**100 in e[3:10**100] # Not touched as expected
False
>>>
```

### Just as if we had more memory that could be potentially stored in all the transistors in the history of human kind combined and multiplied by various orders of magnitude at our disposal for this mundane apparently pointless task.

I know, it is amazing.

### Ok... so what about the len of this slice?

Ah yeah, about that...:

```python
>>> len(e[3:10**100])
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
>>>
```

I hear you, it should output some huge number fairly close to
`10**100`. We can work around that, as suggested by the error message:

```python
>>> e[3:10**100].len()
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999997
>>>
```

### That is unpythonic and therefore uncool, please fix it! Not that I'm even interested in this library.

Well, you've read this far so maybe you are a bit interested. Check
the following [stackoverflow
question](https://stackoverflow.com/questions/79805440/in-python-is-there-a-way-to-get-len-with-int-data-type-and-not-and-index-sized-i).

In sum __len__ assumes that the object is stored in memory and it uses
this fact to have highly performant code (remember that C is used
under python's hood) anything larger will not fit on this variable
which makes sense cause there isn't a large enough memory to store the
entire address space that variable can point to.

TLDR: an eset supports __len__ however __len__ is doen't fully support
an eset.

The sys.maxsize is the maximum value for the dunder __len__ method,
anything higher like the following (normally `maxsize == 2**63-1`):

```python
>>> import sys
>>> len(e[:sys.maxsize+1])
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
>>>
```

Will raise the above error. However, this crazy little project doesn't
really use a lot of memory to define an entire enumerated set
(**eset**). In short an **eset** object is just a mathematical object.

In terms of interface `len` is the only aspect I don't think there will
be a way around it any time soon.

### What else? Are there other examples?

Sure, let's try the Wholes **eset** which is essentially the Whole
numbers set.

```python
>>> from esets import Wholes
>>> w = Wholes()
>>> w
<esets.Wholes (0, 1, 2, 3, ...)>
>>>
```

We can actually get the same values as the Evens, by performing a
slice with a step of 2:

```python
>>> w[::2]
<esets.Wholes* (0, 2, 4, 6, ...)>
>>>
```

Other multiples can actually be obtained from this, say multiples of
7:

```python
>>> w[::7]
<esets.Wholes* (0, 7, 14, 21, ...)>
>>>
```

### Is there an **eset** where we can contruct the multiples from the start?

I thought you'd never ask:

```python
>>> from esets import Multiples
>>> m = Multiples(7)
>>> m
<esets.Multiples (0, 7, 14, 21, ...)>
>>>
```

### What about the Integers?

Here you go:

```python
>>> from esets import Integers
>>> i = Integers()
>>> i
<esets.Integers (0, 1, -1, 2, ...)>
>>>
```

Note that the negatives can be extracted like this:

```python
>>> i[2::2]
<esets.Integers* (-1, -2, -3, -4, ...)>
>>>
```

### How about arithmetic progressions

No sweat:

```python
>>> from esets import IntArithProg
>>> IntArithProg(5,4)
<esets.IntArithProg (4, 9, 14, 19, ...)>
>>> IntArithProg(-4,10)
<esets.IntArithProg (10, 6, 2, -2, ...)>
>>> IntArithProg(-4,10)[:10**4]
<esets.IntArithProg* (10, 6, 2, -2, ..., -39974, -39978, -39982, -39986)>
>>> IntArithProg(-4,10)[:10**4][::-5]
<esets.IntArithProg* (-39986, -39966, -39946, -39926, ..., -66, -46, -26, -6)>
>>>
```

### Hmmm... What about the Squares, as in Galileo's paradox?

I'm way ahead of you:

```python
>>> from esets import Squares
>>> s = Squares()
>>> s
<esets.Squares (0, 1, 4, 9, ...)>
>>>
```

Note that you can technically convert to a list or tuple (i.e. expand
into memory) at any point, just be really careful when doing so,
because you may run out of memory quickly. Converting a slice is a no
brainer:

```python
>>> S = list(s[:10])
>>> S
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
>>>
```

Converting the entire set... just don't ;-)

### All this looks way to academic. Is there more? Something more applied?

Yep and it may pay off big time. But we'll leave it here for now.

Just as a teaser consider the following; In many fields of study using
a relative error that is 10% or under is usually good enough. When
enumerating we are interested in an absolute error, anything different
from zero is completely wrong (even if it is an error of
1). Mathematical precision is of the upmost importance.

Consider the following:

```python
>>> import sys
>>> from math import factorial
>>> h=factorial(10**4)
>>> sys.set_int_max_str_digits(50000)
>>> print(len(str(h)))
35660
>>> print(str(h)[:3])
284
>>>
```

This means that `10000!` is around `2.8*10**35659`, one may be tempted
to say that the error starts from the second decimal on, which is
technically true (when using a relative error context), however that
happens to be more than 35 thousand orders of magnitude wrong in terms
of the absolute error!!

Please take a moment to contemplate this, it is not something that is
off by 35 thousand, that is just 4 orders of magnitude (`10**4`) the
error is in fact 35 thousand orders of magnitude (`10**35000`) even
there it is actually off by about a googol to the six power
(`(10**100)**6==10**600`) look how tiny that is in comparison to
`10**35000`. This is a taste of combinatorial explosion.

We can actually do a:

```python
>>> from esets import Wholes
>>> w = Wholes()
>>> w[:h] #doctest:+ELLIPSIS
<esets.Wholes* ...
>>>
```

I'm deliberately not printing that last line but the eset can take
it. The point is, **esets** can somewhat tame these kinds of
problems. There is a format function if you want to get a sense of it
(it is the one used on the repr):

```python
>>> w.format_funct(factorial(10**4))
'2.8462...00000e+35659'
>>>
```

Do note that:

```python
>>> w[:h].len() == h
True
>>>
```

That number (`h`) when storing it may look like a relatively small
file (about 16kB):

```python
>>> sys.getsizeof(factorial(10000))
15820
>>>
```

A huge number can be a small file. It begs the question, can files be
looked as index numbers from some **eset**?

This is actually a prelude of what is coming next, combinatorial
esets. I hope that this introduction got you in the right mindset for
using this library.

Before going into outrageously large numbers, first take a look into
the [FLOAT64S.md](FLOAT64S.md) for an eset that enumerates all the 64
bit floats.

And for the combinatorial esets themselves, permutations,
combinations, arrangements, subsets, integer partitions and set
partitions, all addressable by index with no enumeration involved, see
[COMBINATORICS.md](COMBINATORICS.md).

## Is there anything like this already out there? (Prior art)

Sort of, but nothing quite does what an **eset** does.

* [`itertools`](https://docs.python.org/3/library/itertools.html)
  (stdlib) gives you lazy infinite sequences (`count`, etc.) but they
  are plain iterators: no indexing, no slicing.

* [`iteration_utilities`](https://github.com/MSeifert04/iteration_utilities)
  is the closest match on the surface. Its `Iterable`/`InfiniteIterable`
  classes support `__getitem__` with both ints and slices, even on
  infinite iterables, e.g. `Iterable.from_count()[:4]`. But looking at
  how `getitem` is actually implemented
  ([`_additional_recipes.py`](https://github.com/MSeifert04/iteration_utilities/blob/master/src/iteration_utilities/_additional_recipes.py))
  it reduces to `itertools.islice` plus a C-level `nth` helper
  ([`nth.c`](https://github.com/MSeifert04/iteration_utilities/blob/master/src/iteration_utilities/_iteration_utilities/nth.c))
  whose loop is:

  ```c
  for (idx = 0; idx <= self->index || self->index < 0;) {
      item = Py_TYPE(iterator)->tp_iternext(iterator);
      ...
  }
  ```

  That is, it calls `next()` on the underlying iterator `idx` times.
  It's lazy in that it doesn't pre-materialize a list, but access is
  still `O(n)` in the index. `Iterable.from_count()[10**100]` would
  try to advance a counter `10**100` times rather than return
  instantly.

  An **eset** never walks anything. `internal_direct_function` is
  pure arithmetic on the index:

  ```python
  def internal_direct_function(self, i):
      return self.direct_function(self.start + i * self.step)
  ```

  which is why `w[3:10**100]` and `e[:10**10:3][::-5]` return
  immediately in the examples above: slicing composes `start`/`stop`/
  `step` algebraically into a new `eset`, it never touches an
  underlying element. `iteration_utilities` can't do that slice in
  finite time for a formula-defined infinite sequence with a
  googol-sized bound; it would try to actually call `next()` that many
  times.

  | | `iteration_utilities` | `esets` |
  |---|---|---|
  | Indexing strategy | walk the iterator `idx` times (`next()` in a loop) | evaluate `direct_function(start + i*step)` directly |
  | Cost of `x[10**100]` | would not finish in your lifetime | instant |
  | What a slice produces | a new lazy *iterator* wrapping `islice` | a new `eset` with recomputed `start`/`stop`/`step`, still `O(1)`-indexable |
  | Requires | any iterable/generator, no closed form needed | an explicit direct function + inverse function per eset |

  The trade-off is real: `iteration_utilities` works on any iterable
  or generator pipeline with no math required from the user. An
  `eset` only works when you can supply a direct formula and its
  inverse, but in exchange it gets true `O(1)` random access and
  slicing at arbitrary scale, which `iteration_utilities` structurally
  cannot offer for formula-defined infinite sequences.

* [SymPy's `sympy.series.sequences`](https://docs.sympy.org/latest/modules/series/sequences.html)
  (`SeqFormula`, `SeqPer`, etc.) are formula-defined, lazily evaluated,
  indexable/sliceable sequences, including infinite ones. Conceptually
  the closest relative of the direct-function idea here, though it's
  symbolic/CAS-flavored rather than a general ABC for defining
  arbitrary bijective esets.

* The [combinatorial number system ("combinadics")](https://en.wikipedia.org/wiki/Combinatorial_number_system)
  (also `more_itertools.nth_combination`) maps an integer index
  directly to the *k*-th combination/permutation without generating
  the ones before it. This is the same direct-function idea applied to
  combinatorics, and is the direction
  [lib/ecombinatorics.py](lib/ecombinatorics.py) is heading -- with one
  caveat the `O(1)` framing above glosses over: it's `O(1)` in the
  index, not in `n` (the size of what's being permuted/combined/...),
  since ranking/unranking a combinatorial structure is real
  algorithmic work in a way `2 * i` isn't. See
  [COMBINATORICS.md](COMBINATORICS.md#a-note-on-speed-upfront) for the
  actual complexity, which is polynomial in `n`, not constant.

### BEset, Eset, and EMap: what's actually underneath?

[eset.py](eset.py) actually splits that ABC in two. `BEset` (the
"blind" eset) is the foundation: indexing, slicing, iteration, `repr`,
the `__len__`/`.len()` split for numbers too large for `__len__` to
return -- everything except knowing whether a given value belongs to
it. That last part is deliberately missing: `BEset.__contains__` is
explicitly disabled, on purpose, not merely unimplemented:

```python
>>> from eset import BEset
>>> class BlindSquares(BEset):
...     def direct_function(self, i):
...         return i * i
...     def stop_init(self):
...         return None
...
>>> bs = BlindSquares()
>>> bs
<esets.BlindSquares (0, 1, 4, 9, ...)>
>>> bs[5]
25
>>> bs[2:6]
<esets.BlindSquares* (4, 9, 16, 25)>
>>> 25 in bs
Traceback (most recent call last):
...
TypeError: Membership check explicitly disabled on besets
>>>
```

A `BlindSquares` can hand you the 6th square instantly and slice
itself, but asking "is 25 a square?" is a different, harder question
(the inverse function has to exist and actually be checked), and a
`BEset` makes no promise about it at all.

Squares are actually a bit too easy an example, though: an inverse
(`sqrt`, rounded and checked) obviously exists, so `BlindSquares` not
offering `contains()` reads as a choice rather than a necessity. The
case `BEset` genuinely earns its keep is a relationship you don't know
how to invert at all, a hash function being the textbook example:

```python
>>> import hashlib
>>> class Sha256Hashes(BEset):
...     def direct_function(self, i):
...         return hashlib.sha256(str(i).encode()).hexdigest()
...     def stop_init(self):
...         return None
...
>>> sh = Sha256Hashes()
>>> sh[0]
'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'
>>> sh[5]
'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d'
>>> sh[2:4]
<esets.Sha256Hashes* (d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35, 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce)>
>>> 'some digest' in sh
Traceback (most recent call last):
...
TypeError: Membership check explicitly disabled on besets
>>>
```

The i-th SHA-256 digest is instant to compute, same as a square. But
there's no `sqrt` to reach for here: recovering `i` from a digest
means brute-forcing candidates, there's no known shortcut, that's the
entire point of a cryptographic hash function. `BlindSquares` chooses
not to define `contains()`; `Sha256Hashes` simply has nothing to
define it with. `BEset` doesn't distinguish between those two cases,
and that's the right call: whether an inverse merely wasn't written or
provably can't be written efficiently, the honest answer is the same
disabled `__contains__`, not a `contains()` that silently loops
forever or lies.

`Eset` is the ABC that adds that promise on top, for the (much more
common) case where an inverse genuinely does exist: `contains`/
`index`/`__contains__`, built on top of `inverse_function`. Every
concrete eset used throughout this file, `Evens` included, is an
`Eset`, not a bare `BEset`.

Writing a whole subclass is not the only way to get there, though. If
all you need is a one-off eset from plain functions, `EMap` builds an
`Eset` directly from a direct function, its inverse, a contains check,
and a base eset (just for sizing, via its `.len()`):

```python
>>> from eset import EMap
>>> from esets import Wholes
>>> e = EMap(lambda i: 2 * i, lambda v: v // 2,
...          lambda v: False if not isinstance(v, int) else None, Wholes())
>>> e
<esets.EMap (0, 2, 4, 6, ...)>
>>> e[10:20]
<esets.EMap* (20, 22, 24, 26, ..., 32, 34, 36, 38)>
>>>
```

Recognized as an `EMap`, not an `Evens`, but behaving identically --
no subclass required. See docTest.txt for a fuller walkthrough
(including why the contains function returns `None` rather than
`True` for a match).

## TODO:

* Describe how to create and `eset`.
* Implement other esets.
* ~~Start development with combinators, permutators and other ones.~~
  See [COMBINATORICS.md](COMBINATORICS.md).
* How do these compare with lists, tuples, sets etc.?
* Compare with itertools (once the above is ready).
