# esets

The datastructure that nobody asked for is finally here. (beta)

## What is it? (An informal introduction)

**esets** stands for enumerated sets. They can handle arbitrarily
  large sets, and even represent infinite numerable sets (like the set
  of even numbers). This is possible since in essence they are lazy
  generated sequences.

In a sense, this could be described like a memoryless data structure.
Something where the structure is in memory but not the data. The data
is directly generated from the structure as soon as it is needed so
there is no need to store the entirety of the data on memory. Despite
this you may access the data via indexing, and operations such as
slicing are accessible.

### But don't indices relate to locations in memory in sequences?

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

```
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

```
>>> e = Evens()
>>> e
<esets.Evens (0, 2, 4, 6, ...)>
>>>
```

Here the ellipsis (`...`) at the end means that the sequence goes on
forever. Any positive integer is there, as long as in can be stored in
memory we can check it e.g.:

```
>>> a=4732868736587936587436587346587356843765438756438756823764823746238764283764237846238746238746237842378672385687235623746238764238746873246
>>> a in e
True
>>> a+1 in e
False
>>>
```

### So what about it's len?

About that:

```
>>> len(e)
Traceback (most recent call last):
...
ValueError: Aleph_0 infinite
>>>
```

### This is obviously wrong, we don't have an infinite amount of memory to store the entire set!!

Correct, we aren't. It is a lazy evaluated sequence, and discrete math
is behind this.

In the spirit of Georg Cantor's work we are simply establishing a
relationship between the Even numbers and the Whole numbers (0, 1, 2,
...) where the later serve as our indices.

```
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

```
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

```
>>> e.index(42)
21
>>>
```

### So it is just a convoluted way of doing some trivial math?

At first glance yes. But kindly note that even for this trivial
example some non-trivial operations are happening behind the
hood. Check out the following:

```
>>> e[:10**10:3][::-5]
<esets.Evens* (19999999998, 19999999968, 19999999938, 19999999908, ..., 48, 18)>
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

```
>>> e[3:10**100]
<esets.Evens* (6, 8, 10, 12, ..., 19999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999996, 19999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999998)>
>>>
```

So naturally here:

```
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

```
>>> len(e[3:10**100])
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
>>>
```

I hear you it should output some huge number fairly close to
`10**100`. We can work around that, as suggested by the error message:

```
>>> e[3:10**100].len()
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999997
>>>
```

### That is unpythonic and therefore uncool, please fix it! Not that I'm even interested in this library.

Well, you've read this far so maybe you are a bit interested. Check
the following [stackoverflow
question](https://stackoverflow.com/questions/79805440/in-python-is-there-a-way-to-get-len-with-int-data-type-and-not-and-index-sized-i).

TLDR: __len__ assumes that the object is stored in memory and it uses
this fact to have highly performant code (remember that C is used
under python's hood) anything larger will not fit on this variable
which makes sense cause there isn't a large enough memory to store the
entire address space that variable can point to.

The sys.maxsize is the maximum value for the dunder __len__ method,
anything higher like the following (normally `maxsize == 2**63-1`):

```
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

```
>>> from esets import Wholes
>>> w = Wholes()
>>> w
<esets.Wholes (0, 1, 2, 3, ...)>
>>>
```

We can actually get the same values as the Evens, by performing a
slice with a step of 2:

```
>>> w[::2]
<esets.Wholes* (0, 2, 4, 6, ...)>
>>>
```

Other multiples can actually be obtained from this, say multiples of
7:

```
>>> w[::7]
<esets.Wholes* (0, 7, 14, 21, ...)>
>>>
```

### Is there an **eset** where we can contruct the multiples from the start?

I thought you'd never ask:

```
>>> from esets import Multiples
>>> m = Multiples(7)
>>> m
<esets.Multiples (0, 7, 14, 21, ...)>
>>>
```

### What about the Integers?

Here you go:

```
>>> from esets import Integers
>>> i = Integers()
>>> i
<esets.Integers (0, 1, -1, 2, ...)>
>>>
```

Note that the negatives can be extracted like this:

```
>>> i[2::2]
<esets.Integers* (-1, -2, -3, -4, ...)>
>>>
```

### Hmmm... What about the Squares, as in Galileo's paradox?

I'm way ahead of you:

```
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

```
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

```
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

```
>>> from esets import Wholes
>>> w = Wholes()
>>> w[:h] #doctest:+ELLIPSIS
<esets.Wholes* ...
>>>
```

I'm deliberately not printing that last line but the eset can take
it. The point is, **esets** can somewhat tame these kinds of problems.

Do note that:

```
>>> w[:h].len() == h
True
>>>
```

That number (`h`) when storing it may look like a relatively small
file (about 16kB):

```
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

## TODO:

* Expand this introduction.
* Describe how to create and `eset`.
* Implement other esets (rationals?, floating points?)
* Start development with combinators, permutators and other ones.
* How do these compare with lists, tuples, sets etc.?
* Compare with itertools (once the above is ready).