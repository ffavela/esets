# esets

The datastructure that nobody asked for is finally here.

## What is it? (An informal introduction)

**esets** stands for enumerated sets. They can handle arbitrarily
  large sets, and even represent infinite numerable sets (like the set
  of even numbers). This is possible since in essence they are lazy
  generated sequences.

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
```

### The relationship is clear for any index value just double it to get the respective Evens value right?

Basically yes, and for the reverse we can use dividing by two:

```
>>> e.index(42)
21
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
anything higher like (normally `maxsize == 2**63-1`):

```
>>> import sys
>>> len(p[:sys.maxsize+1])
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
```

However, this crazy little project doesn't really use a lot of memory
to define an entire enumerated set (**eset**). In short an **eset**
object is just a mathematical object.

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
```

Other multiples can actually be obtained from this, say multiples of
7:

```
>>> w[::7]
<esets.Wholes* (0, 7, 14, 21, ...)>
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
```

Note that the negatives can be extracted like this:

```
>>> i[2::2]
<esets.Integers* (-1, -2, -3, -4, ...)>
```

### All this looks way to academic. Is there more? Something more applied?

Yep. But we'll leave it here for now.

Just as a teaser:

```
>>> import sys
>>> from math import factorial
>>> h=factorial(10**4)
>>> sys.set_int_max_str_digits(50000)
>>> print(len(str(h)))
35660
>>> print(str(h)[:3])
284
```

This means that `10000!` is around `2.8*10**35659`, one may be tempted
to say that the error starts from the second decimal on, which is
technically true, however that happens to be more than 35 thousand
orders of magnitude wrong!!

We can actually do a:

```
>>> from esets import Wholes
>>> w = Wholes()
>>> w[:h]
...
```

I'm deliberately not printing that last line but the eset can take it.

In short, it is important to be precise when enumerating because the
numbers refer to different elements even if the "error" is only one.

That number (`h`) when storing it may look like a relatively small
file this is actually a prelude of what is comming next.

## TODO:

* Expand this introduction.
* Implement other esets (rationals?, floating points?)
* Start development with combinators, permutators and other ones.
* How do these compare with lists, tuples, sets etc.?