# esets

The datastructure that nobody asked for is finally here.

## What is it?

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
>>> for i in range(10):
...     print(i, e[i])
... 
0 0
1 2
2 4
3 6
4 8
5 10
6 12
7 14
8 16
9 18
```

### The relationship is clear for any index value just double it to
get the respective Evens value right?

Basically yes, and for the reverse we can use dividing by two:

```
>>> e.index(42)
21
```

### So it is just a convoluted way of doing some trivial math?

At first glance yes. But kindly note that even for this trivial
example some non-trivial operations are happening behind the
hood. Let's first perform a slice, let's use a googol:

```
>>> e[3:10**100]
<esets.Evens* (6, 8, 10, 12, ..., 19999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999996, 19999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999998)>
```

So naturaly here ... to be continued ...