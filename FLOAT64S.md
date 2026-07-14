# Float64s eset

An eset case study. Floats are of great importance specifically for
scientific computing, despite initial push backs from people like John
von Neumann (just one of the smartest humans who has ever lived, so
no pressure...) the floating point standard has prevailed.

Thanks to the work of brilliant engineers like Bill Kahan, a lot of
work from scientists and engineers was possible. The standard has
proven its usefulness just by the sheer amount of time and people that
have used it not to mention the amount of critical systems that rely
on it. It is supported at the hardware level so calculations are
really fast.

I'm writing this section out of admiration for the standard, and while
I am really opinionated regarding concepts like the "Real" numbers as
you may read further ahead. I think floats are an honest approach to
represent non integer numbers considering the physical constraints we
face with digital computers. Kindly note that I may highlight various
rough edges, but that is because this (eset) approach makes it really
easy to visibilize them, and for me this only adds to the
impressiveness of the standard that it can work so well.

Yes there may be a need for other case studies like John L. Gustafson's
Unums which may come in the future. But for now, a 64 bit float
eset is the main topic.

### So in other words a list of floats?

No not a list, but the list. All the 64 bit floats (a.k.a
doubles). All of them!!

### But what about continuity and uncountable infinites?

Reals aren't real, floats aren't Real, floats are real.

### What?!

Digitally speaking, we cannot realistically store a single Real
number. Not even with the combined cumulative storage capacity of all
the history of human kind. Granted we can define them through a
process, and perform an abstract definition, even have an arbitrary
precision, but that doesn't change the fact that we can't store a
single one on a digital binary (or ternary or whichever base)
computer. The Real numbers are a mathematical concept but (in my
opinion) it is an unfortunate naming convention, it tags them as in
every sense of the word as real, the noun is commonly also interpreted
as an adjective. You can still call them Real, but at least on this
text mentally remove the "real" tag to avoid any confusion.

Sixty four bit floats on the other hand are a different story. They
can represent up to `2**64 == 18446744073709551616 ~ 1.84e+19`
different values, the IEEE 754 specifies a format for them. One bit
for a sign, 11 for an exponent and 52 for a significand (sometimes
called fraction or mantissa). The exponent bits have a 1023 bias,
i.e. the interpreted exponent is exponent-1023.

### Wait under the same logic the Rationals also have an issue

Yes and no. If a set has at least one member that can **only** be
represented using an infinite amount of memory, then that set has this
issue. A Rational number would need an infinite amount of information
when expressed in its decimal expansion. Granted you may say that after
a particular decimal all the rest of the digits are (say 0) and
therefore there is no need to store it, we could let that pass since
at least numerically in terms of magnitude it is indistinguishable
from any other expansion that decides to use more trailing
zeroes. Like in:

```
1/4 == 0.25 == 0.250 == 0.2500 ...
```

This is the famous termination after a finite number of digits
argument.

But what happens if the trailing number is not zero (like a
1) the magnitude argument collapses since:

```
1/9 != 0.1 != 0.11 != 0.111 ...
```

Because (where ... mean infinite expansion of ones):

```
1/9 == 0.1111...
```

So the previous argument for the trailing zeroes plays against us since:

```
0.1   == 0.10   != 0.1...
0.11  == 0.110  != 0.111...
0.111 == 0.1110 != 0.1111...
.
.
.
```

This is the other famous case where the same sequence of numbers
repeats over and over. Kindly note that they are essentially the same
case (in the former it was trailing 0s while the latter trailing 1s).

There are at least 2 equivalent ways to circumvent this unrealistic
situation and use a finite amount of information. Both require the use
of a process in its definition:

1) All Rationals have a repeated decimal expansion so we can save the
non repeated part in a finite amount of memory. Then save the part
that repeats (a single repetition) and then save a process that uses
this data to get any decimal value.

2) Rationals can also be described as a quotient, that is a division
of two integer numbers. A numerator that can be an integer and a
denominator that can be any integer except zero. Those two values use
a finite amount of information, the process in this case is a
division.

Note that in both cases the process or function definition can be
stored in a finite amount of memory. Whereas the infinite decimal
expansion can't. Note that Irrationals such as `sqrt(2)` do not need
an infinite amount of information to be defined. The issue only comes
when trying to use their decimal expansion.

All that just to say that we can store any single Float, because the
elements of this set can be represented in a finite amount of memory.
We could even omit the use of a process for defining them!

If we were determined enough we could even store all of them given the
current storage capacity of mankind (as of writing this), that'll take
a significant portion but it is currently possible.

### Storing all 64 bit floats is definitively a terrible idea

Agree, let's do it!!

Via an eset of course ;-)

There is already an implementation of this so you can simply run the
following:

```python
>>> from esets import Float64s
>>> f64s = Float64s()
>>> f64s
<esets.Float64s (0, -0, 4.9406564584124654e-324, -4.9406564584124654e-324, ..., inf, -inf, nan, -nan)>
>>>
```

Note that the repr (the above printout) uses a 17 digit format for
expressing the f64s in order to view the full resolution of the
floats.

### Wait a negative zero? Also nan is literally "not a number"...

Correct, but it is a float. IEEE 754 specifies also `0`, `-0` (as odd
as it may look), `inf`, `-inf`, `nan`, `-nan`.

```python
>>> f64s[-6:]
<esets.Float64s* (1.7976931348623157e+308, -1.7976931348623157e+308, inf, -inf, nan, -nan)>
>>>
```

There is actually a function that can help visualize the binary
representation, it is a tuple that has 3 values that represent as
integers the sign, exponent and significand. This tuple is called tpl
and we can also see the respective binary representation:

```python
>>> f64s.float2tpl(0)
(0, 0, 0)
>>> f64s.float2bintpl(0)
('0', '00000000000', '0000000000000000000000000000000000000000000000000000')
>>> f64s.float2tpl(-float(0))
(1, 0, 0)
>>> f64s.float2bintpl(-float(0))
('1', '00000000000', '0000000000000000000000000000000000000000000000000000')
>>> f64s.float2tpl(float('inf'))
(0, 2047, 0)
>>> f64s.float2bintpl(float('inf'))
('0', '11111111111', '0000000000000000000000000000000000000000000000000000')
>>> f64s.float2tpl(float('-inf'))
(1, 2047, 0)
>>> f64s.float2bintpl(float('-inf'))
('1', '11111111111', '0000000000000000000000000000000000000000000000000000')
>>> f64s.float2bintpl(float('nan'))
('0', '11111111111', '0000000000000000000000000000000000000000000000000001')
>>> f64s.float2bintpl(float('-nan'))
('1', '11111111111', '0000000000000000000000000000000000000000000000000001')
>>>
```

The IEEE is a bit vague regarding the nans, there can be many more than
the 2 we've presented and the default base values can be
different. For this implementation and for the sake of simplicity,
only 2 are the accepted values for our Float64s eset.

### So what is the len?

As seen on the README file:

```python
>>> len(f64s)
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
>>>
```

But we can use:

```python
>>> f64s.len()
18437736874454810628
>>>
```

Using this we can calculate the number of bytes required to store
them, 64 bits are 8 bytes, so:

```python
>>> f64s.len()*8 # Bytes
147501894995638485024
>>> f64s.len()*8//10**18 # Exabytes
147
>>> f64s.len()*8//2**60 # Exbibytes
127
>>>

```

So we need 147 exabytes, or a bit more precisely, 127 exbibytes. A quick
comparison, a laptop hard drive has around 1TB, 1EB ~ `10**6` TB. So
around 100 million of these would be required to store all the 64 bit
floats.

### Yeah impressive, but wait that len is not `2**64`

Yeah, that is actually:

```python
>>> 2*(2**63-2**52+2) == 18437736874454810628 == f64s.len()
True
>>>
```

The Float64s eset is actually built on top a tpl version called
Float64_tpls:

```python
>>> from esets import Float64_tpls
>>> f64tpls = Float64_tpls()
>>> f64tpls
<esets.Float64_tpls ((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1), ..., (0, 2047, 4503599627370494), (1, 2047, 4503599627370494), (0, 2047, 4503599627370495), (1, 2047, 4503599627370495))>
>>>
```

so we can simply get the index of the `-nan` plus one to get that
precise number too:

```python
>>> f64tpls[:f64tpls.index((1, 2047, 1))+1].len()
18437736874454810628
>>>
```

### Ok back to the Float64s, what if I just want the positives?

As in the case of the integers the floats are "folded" with
alternating positive and negative values, so we can extract them via a
simple slice with a step of two. Something similar can also be done
with the negatives but using the start as 1:

```python
>>> pf64s = f64s[::2]
>>> pf64s
<esets.Float64s* (0, 4.9406564584124654e-324, 9.8813129168249309e-324, 1.4821969375237396e-323, ..., 1.7976931348623155e+308, 1.7976931348623157e+308, inf, nan)>
>>> nf64s = f64s[1::2]
>>> nf64s
<esets.Float64s* (-0, -4.9406564584124654e-324, -9.8813129168249309e-324, -1.4821969375237396e-323, ..., -1.7976931348623155e+308, -1.7976931348623157e+308, -inf, -nan)>
>>>
```

And as expected their lens are half of the total:

```python
>>> pf64s.len()
9218868437227405314
>>> nf64s.len()
9218868437227405314
>>> f64s.len() == 2*pf64s.len() == 2*nf64s.len()
True
>>>
```

### Is there any real application for this?

Not that I can think of right now. This is also just an academic
exploration. But it does start to show some weird aspects about
floats. Take the first float after zero and multiply it by 1.4, it turns out that:

```python
>>> 1.4 * pf64s[1] == pf64s[1]
True
>>>
```

That is a number greater than zero (also that is not something weird
like an `inf` or a `nan`) multiplied by something greater than 1 is
the same number!

That doesn't happen with the Real numbers, in that case it doesn't
even make sense to conceive of the first number after zero. It just
doesn't exist. And if you would grab any Real number (excluding zero)
none would satisfy the above relationship. Also for any `n` say 1000,
the average of 2 consecutive positive floats satisfy:

```python
>>> n = 1000
>>> (pf64s[n]+pf64s[n+1])/2 == pf64s[n]
True
>>>
```

Note that we are using the `==` which is normally a big no NO when
dealing with floats. But it is ok, we know what we are doing (I
think...).

We could look into more weirdness in how floats behave, but let's move
forward. The key takeaway is simply to note that they are in fact
incredibly useful but we need to be aware of their limitations. It
doesn't matter how many bits are used, they simply aren't continuous
and operating with them can lead to information loss. That isn't bad
for many intended purposes.

### But?

Yeah there is a but.

But for the case of enumerating, rounding-off can give completely
different results. Granted floats aren't used for that normally, so
for all intended purposes we are safe.

Let's explore some other properties. An eset has the `__contains__`
method so we can use the `in` operation:

```python
>>> 0.0 in pf64s
True
>>> 0.0 in pf64s[1:]
False
>>> -5 in pf64s
False
>>>
```

That ^ is kind of dumb I know but worth showing it also:

```python
>>> float('inf') in pf64s
True
>>> float('nan') in pf64s
True
>>> 3.141592 in pf64s # pi approx. Do you see anything odd?
True
>>> 3 in pf64s # Kind of obvious but yeah an integer is there
True
>>>
```

### Elaborate on the odd part on the pi approx.

It may be more clear seeing the following:

```python
>>> 0.2 in pf64s # Still odd, I'll explain below
True
>>>
```

Let's print it with 17 digits to better explain:

```python
>>> format(0.2, '.17g')
'0.20000000000000001'
>>>
```

Yep ^, 0.2 (a.k.a 1/5) cannot be properly represented in
binary. Python seems to be cheating here, our value is converted to a
float i.e. 0.2 turns into a 0.20000000000000001 and then it says yeah
that float value I just converted to (not the one you actually asked about)
is present. This would happen on other programming languages by the
way, that conversion is done under the hood and is actually
expected. But in this particular case we need to highlight it, Real
values are rounded to the nearest float. And on the aforementioned
`pi` approximation:

```python
>>> format(3.121592, '.17g')
'3.1215920000000001'
>>>
```

There it is, a bunch of zeroes and then a one, which differs by a tiny
amount from the `pi` approximation. So yeah floats give approximations
to values that are already approximations, even when using a finite
decimal expansion. Yes there are other objects we could use instead
for "containing" those values if we really cared about those
particular issues but the main interest is the Float64s eset.

Coming back to the 0.2 (1/5) case, we can make a fairer check if we
use fractions, which is accepted by the `__contains__` method so:

```python
>>> from fractions import Fraction
>>> Fraction(1, 5) in pf64s
False
>>>
```

This way, we have avoided the float conversion and it clearly shows a
hole in the floats. Fractions are essentially Rational numbers, and
regarding the previous discussion of the Reals, yes the tag is more
appropriate.

Note index method is actually able to get the integer value of any float:

```python
>>> pf64s.index(2.718281)
4613303443449361558
>>>
```

That number is an approximation of e. And for the positive floats,
that corresponds to the 4613303443449361558 positive float. The next
one is:

```python
>>> pf64s[pf64s.index(2.718281)+1]
2.7182810000000006
>>>
```

We can simply get a slice starting from the first approximation:

```python
>>> pf64s[pf64s.index(2.718281):]
<esets.Float64s* (2.7182810000000002, 2.7182810000000006, 2.7182810000000011, 2.7182810000000015, ..., 1.7976931348623155e+308, 1.7976931348623157e+308, inf, nan)>
>>>
```

Also define the stop index to be the next number in the least
significant digit resulting in 2.718282, saving that eset into a
variable called `sliver`:

```python
>>> sliver = pf64s[pf64s.index(2.718281):pf64s.index(2.718282)]
>>> sliver
<esets.Float64s* (2.7182810000000002, 2.7182810000000006, 2.7182810000000011, 2.7182810000000015, ..., 2.7182819999999981, 2.7182819999999985, 2.718281999999999, 2.7182819999999994)>
>>>
```

We can even get the len:

```python
>>> sliver.len()
2251799813
>>>
```

A lot of 64 bit floats on that "small" slice. Let's search for the
index on that `sliver` variable of the value of `e` directly from the
math library.

```python
>>> from math import e
>>> e
2.718281828459045
>>> sliver.index(e)
1865523923
>>>
```

So as expected:

```python
>>> sliver[1865523923]
2.718281828459045
>>>
```

### Why not simply use `math.isclose` and be happy?... Duh!!

Fair point, when comparing floats it is generally a bad idea to use
`==` whereas `math.isclose` should be the way to go. But this is an
exploration of the standard where we want to highlight some of the
limitations it has and also emphasize the granularity of the possible
values.

Let's make a comparison between 2 floats say:

```python
>>> import math
>>> x = 4503599627370496.0
>>> y = 4503599627370496.5
>>> math.isclose(x, y)
True
>>>
```

So yeah they are relatively close we can see that, however please note
the following:

```python
>>> x == y
True
>>>
```

Which makes no sense, they are clearly different right?! Well, it
turns out that:

```python
>>> x == float(2**52)
True
>>>
```

And as we saw previously on this text, there is no way to express a
decimal part from here on. Just for accentuating this further:

```python
>>> float(2**52) == float(2**52) + 0.5
True
>>>
```

So what happened is that `y` was simply rounded down to `x` before we
invoked `math.isclose`, so yes technically a number is always close to
itself so it returned `True`. Note that for this case using `==` for
floats actually clarifies what is happening while `math.isclose`
doesn't.

Note that the very next value is (see previously for the why):

```python
>>> y = x + 1
>>> x == y
False
>>>
```

And to make it obvious:

```python
>>> y - x
1.0

```

So just 2 values that differ by one, not by 0.5, not by ten to the
minus something, they differ by one. If I call `math.isclose`, will it
return `True` or `False`? Let's find out:

```python
>>> math.isclose(x, y)
True
>>>
```

Now this may or may not be what you expected, but the fact that I got
different answers when asking is a bit of an issue.

### Ok but you can tweak `math.isclose`

Indeed, from the documentation
[math.isclose](https://docs.python.org/3/library/math.html#math.isclose)
and the corresponding [PEP 485](https://peps.python.org/pep-0485/) we
see that this is how it can be called in its general form:


```python
math.isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0)
```

So there it is, it uses a `rel_tol` (relative tolerance) which is
something that scales with the size of the numbers.

If there are no errors, then the function behaves as:

```python
abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
```

The `abs_tol` (absolute tolerance) is usually relevant for comparing
values close to zero (source; I just googled it).

This behavior may turn into an unpleasant surprise when working with a
grid or a quadtree with fixed bin sizes where some bins are far away
or perhaps you are performing additions and it may be important to
know when they stop being relevant because they are getting rounded
off.

We note that `math.isclose` scales and we can turn it off quite easily
by setting `rel_tol` to zero and `abs_tol` to a desired value (say
0.5) given the minimum resolution we desire for our grid. Using this
we finally get:

```python
>>> math.isclose(x, y, rel_tol=0, abs_tol=0.5)
False
>>>
```

That is, for our hypothetical grid, we can't resolve values that far
apart; we should handle that appropriately, or our computations will
spit out silly results.

We can visualise the float values quite easily by using slicing on the
positive floats eset:

```python
>>> pf64s[pf64s.index(float(2**52)):pf64s.index(float(2**53))]
<esets.Float64s* (4503599627370496, 4503599627370497, 4503599627370498, 4503599627370499, ..., 9007199254740988, 9007199254740989, 9007199254740990, 9007199254740991)>
>>>
```

It kind of begs the question about the nature of the epsilon, whether
it could be defined in a more general useful form.

### What about the epsilon?

Thank you for asking.

That is actually straightforward we simply find the index of the 1.0
and add one to that index and then take the difference between the
pf64s float on that value and 1.0:

```python
>>> pf64s[pf64s.index(1.0)+1]-1.0
2.220446049250313e-16
>>>
```

No need to do a while loop, just a simple subtraction once we have the
desired index. However, we can actually generalize quite easily to an
epsilon function defined on almost all the floats like the following:

```python
>>> def epsilon(x: float) -> float:
...     pf64s = Float64s()[::2]
...     x = abs(x) # Focusing on the positive floats
...     if x >= pf64s[-3]: # The largest numeric value
...             raise ValueError("Out of bounds")
...     return pf64s[pf64s.index(x)+1] - x
...
>>> epsilon(0)
5e-324
>>> epsilon(1.0)
2.220446049250313e-16
>>> epsilon(2.0)
4.440892098500626e-16
>>> epsilon(5.0)
8.881784197001252e-16
>>> epsilon(100.0)
1.4210854715202004e-14
>>> epsilon(10000.0)
1.8189894035458565e-12
>>> epsilon(10000000.0)
1.862645149230957e-09
>>>
```

It reproduces the expected result for 1.0, also it gives us the value
at basically any other given float.

As mentioned above the total number of positive 64 bit floats is
9218868437227405314 which is approximately 9.2e+18 different
values. Let's say we want a partition of the whole range from 0.0 to the maximum
numeric float value, that could be done by dividing the float range by
the desired value, say `10**6`. However note that the float density is
not actually uniform (see next section), it may be clearer to
partition the positive floats in the index space and sampling every
`10**13` floats (yes every ten trillion) so:

```python
>>> fsample = pf64s[::10**13]
>>> fsample
<esets.Float64s* (0, 4.9406564584124654e-311, 9.8813129168249309e-311, 1.4821969375237396e-310, ..., 1.7900216780780885e+308, 1.7920175183876232e+308, 1.7940133586971579e+308, 1.7960091990066926e+308)>
>>> fsample.len()
921887
>>>
```

We get about a million elements on the `fsample` eset we could use
that to apply a function like `epsilon` on it and perhaps get a better
sense on how `epsilon` behaves throughout the floats.

Also, note the following:

```python
>>> pf64s[-5:]
<esets.Float64s* (1.7976931348623153e+308, 1.7976931348623155e+308, 1.7976931348623157e+308, inf, nan)>
>>>
```

The highest numeric value is 1.7976931348623157e+308.

### Ok so that should be last possible integer it can contain, right?

Yes, but there are integer holes there too.

### Where? How can they be found?

So the significand (the fractional part of the float64) has 52 bits,
any number higher than this (`2**52`) can no longer represent
fractional values -- only integers:

```python
>>> pf64s.float2bintpl(2**52-1)
('0', '10000110010', '1111111111111111111111111111111111111111111111111110')
>>> pf64s.float2bintpl(2**52)
('0', '10000110011', '0000000000000000000000000000000000000000000000000000')
>>> pf64s.float2bintpl(2**52+1)
('0', '10000110011', '0000000000000000000000000000000000000000000000000001')
>>> pf64s.float2bintpl(2**52+2)
('0', '10000110011', '0000000000000000000000000000000000000000000000000010')
>>>
```

Or:

```python
>>> pf64s[pf64s.index(2**52)]
4503599627370496.0
>>> pf64s[pf64s.index(2**52)+1]
4503599627370497.0
>>> pf64s[pf64s.index(2**52)+2]
4503599627370498.0
>>> pf64s[pf64s.index(2**52)+3]
4503599627370499.0
>>>
```

This goes all the way until `2**53`:

```python
>>> pf64s[pf64s.index(2**52):pf64s.index(2**53)]
<esets.Float64s* (4503599627370496, 4503599627370497, 4503599627370498, 4503599627370499, ..., 9007199254740988, 9007199254740989, 9007199254740990, 9007199254740991)>
>>>
```

Notice the lack of decimal values, actually:

```python
>>> 4503599627370496.5 in  pf64s[pf64s.index(2**52):pf64s.index(2**53)]
True
>>> (Fraction(4503599627370496)+Fraction(1/2)) in  pf64s[pf64s.index(2**52):pf64s.index(2**53)]
False
>>>
```

Yep the internal float conversion can try to fool us again but the
Fractions come to the rescue.

### So the integer holes are from `2**53` and on?

Exactly between `2**53` and `2**54` values start jumping in 2s:

```python
>>> pf64s[pf64s.index(2**53):pf64s.index(2**54)]
<esets.Float64s* (9007199254740992, 9007199254740994, 9007199254740996, 9007199254740998, ..., 18014398509481976, 18014398509481978, 18014398509481980, 18014398509481982)>
>>>
```

So:

```python
>>> 9007199254740993 in pf64s[pf64s.index(2**53):pf64s.index(2**54)]
False
>>>
```

Also between `2**54` and `2**55` values start jumping in 4s:

```python
>>> pf64s[pf64s.index(2**54):pf64s.index(2**55)]
<esets.Float64s* (18014398509481984, 18014398509481988, 18014398509481992, 18014398509481996, ..., 36028797018963952, 36028797018963956, 36028797018963960, 36028797018963964)>
>>>
```

### Where do subnormals (a.k.a. denormals) fall here?

So the first subnormal (the exponent bits are zero) is zero and the
last has all ones on the significand that is `2**52-1`, so looking at
the pf64s:

```python
>>> pf64s.tpl2bintpl((0, 0, 2**52-1))
('0', '00000000000', '1111111111111111111111111111111111111111111111111111')
>>> pf64s[:pf64s.f64tpls.index((0, 0, 2**52-1))+1]
<esets.Float64s* (0, 4.9406564584124654e-324, 9.8813129168249309e-324, 1.4821969375237396e-323, ..., 2.2250738585071994e-308, 2.2250738585071999e-308, 2.2250738585072004e-308, 2.2250738585072009e-308)>
>>>
```

The amount of positive subnormals are:

```python
>>> pf64s[:pf64s.f64tpls.index((0, 0, 2**52-1))+1].len()
4503599627370496
>>>
```

And the total (including the negatives) is:

```python
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()
9007199254740992
>>>
```

The total storage capacity to store these is:

```python
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()//8//10**12 # Terabytes
1125
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()//8//2**40 # Tebibytes
1024
>>>
```

So around 1000 of these laptop harddrives, more doable than the entire
64bit floats. But still kind of out of reach through conventional
approaches like using lists or tuples, but definitively reachable via
the Float64s eset B-).

## Has anyone done this before? (Prior art)

The underlying trick, yes, more than once. Wrapping it into an
indexable/sliceable enumerated set of the entire float64 space, not
that I could find.

### The bit trick: well established

Mapping an IEEE 754 bit pattern to a monotonic integer, so that
adjacent floats get adjacent integers, keeps getting independently
reinvented:

* [IEEE 754-2008's `totalOrder`
  predicate](https://en.wikipedia.org/wiki/IEEE_754) formally
  specifies exactly this: a total, monotonic order over all floats,
  including signed zeros and nans.

* [Bruce Dawson's "Comparing Floating Point Numbers, 2012
  Edition"](https://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition/)
  states what he calls the "obvious-in-hindsight theorem": subtract
  the integer representations of two same-sign floats and the
  absolute difference equals 1 plus the number of representable
  floats between them. That is exactly what `f64s.index(a) -
  f64s.index(b)` gives you here, derived independently and for a
  narrower purpose (ULP distance for float comparisons) rather than
  as a general indexable set.

* [Google Test's `FloatingPoint`
  class](https://github.com/google/googletest/blob/main/googletest/include/gtest/internal/gtest-internal.h)
  converts sign-and-magnitude bit patterns to a "biased"
  representation for the same reason: computing ULP distance for
  `AlmostEquals`, with a hardcoded `kMaxUlps` tolerance.

* The [radix-sort float
  trick](https://stereopsis.com/radix.html) (Michael Herf) flips the
  sign bit (positive floats) or all bits (negative floats) to make
  float bit patterns sortable as unsigned integers, the same
  fold-and-bias idea, used to make floats radix-sortable.

* Rust's `f64::total_cmp` (stable since 1.62) implements the IEEE
  `totalOrder` predicate with essentially the same bit manipulation,
  for use as a general-purpose total order, e.g. `sort_by(f64::total_cmp)`.

* `math.nextafter`/`numpy.nextafter` give you the next or previous
  representable float directly from libm, without going through an
  explicit integer index: a narrower, one-step version of the same
  "walk the float lattice" idea.

### What looks new here

None of the above package the trick into a general-purpose
*enumerated set*: something you index (`pf64s[n]`), slice
(`pf64s[a:b]`, even at conceptually googol scale), reverse-lookup
(`.index(val)`), and check membership on (`Fraction(1, 5) in pf64s`),
while deriving properties like the ULP epsilon or the subnormal-region
boundaries purely from index arithmetic. The prior art above is either

1. a **spec** (`totalOrder`), with no indexable-set implementation,
2. a **single-purpose comparison utility** (gtest, Dawson's ULP-diff,
   `nextafter`), a one-shot distance or step rather than a full
   enumerable/sliceable object, or
3. a **sort key transform** (radix sort trick, `total_cmp`), used to
   order an existing collection of floats you already have, not to
   enumerate the entire float64 space as a first-class sequence.

`Float64s` looks like a legitimate, if niche, synthesis: taking the
well known bit-fold/bias trick and wrapping it in the same `eset` ABC
used elsewhere in this repo. That is what lets you do things like
`pf64s[pf64s.index(2**52):pf64s.index(2**53)]` to see the
integer-only gap region, or `fsample = pf64s[::10**13]` to sample a
million-point grid over all positive floats, neither of which the
prior art above supports directly over "all floats" as a set.
