# Float64s eset

An eset case study

### So in other words a list of floats?

No not a list, but the list. All the 64 bit floats (a.k.a
doubles). All of them!!

### But what about continuity and uncountable infinites?

Reals aren't real, floats aren't Real, floats are real.

### What?!

Digitally speaking, we cannot realistically store a single Real
number. Not even with the combined cumilative storage capacity of all
the history of human kind. Granted we can define them through a
process, and perform an abstract definition, even have an arbitrary
precision, but that doesn't change the fact that we can't store a
single one on a digital binary (or ternary or whichever base)
computer. The Real numbers are a mathematical concept but (in my
opinion) it is an unfortunate naming convention, it tags them as in
every sense of the word as real, the noun is comonly also interpreted
as an adjective. You can still call them Real, but at least on this
text mentally remove the "real" tag to avoid any confussion.

Sixty four bit floats on the other hand are a different story. They
can represent up to 2**64 == 18446744073709551616 ~ 1.84e+19 different
values, the IEEE 754 specifies a format for them. One bit for a sign,
11 for an exponent and 52 for a significand (sometimes called fraction
or mantissa). The exponent bits have a 1023 bias, i.e. the interpreted
exponent is exponent-1023.

All that just to say that we can store any single float and also if we
were determined enough we could even store all of them given the
current storage capacity of mankind that'll take a significant portion
but it is currently possible.

### Storing all 64 bit floats is definetively a terrible idea

Agree, let's do it!!

Via an eset of course ;-)

There is already an implementation of this so you can simply run the
following:

```
>>> from esets import Float64s
>>> f64s = Float64s()
>>> f64s
<esets.Float64s (0, -0, 4.9406564584124654e-324, -4.9406564584124654e-324, ..., nan, -nan)>
>>>
```

Note that the repr (the above printout) uses a 17 digit format for
expressing the f64s in order to view the full resolution of the
floats.

### Wait a negative zero? Also nan is literally "not a number"...

Correct, but it is a float. IEEE 754 specifies also `0`, `-0` (as odd
as it may look), `inf`, `-inf`, `nan`, `-nan`.

```
>>> f64s[-6:]
<esets.Float64s (1.7976931348623157e+308, -1.7976931348623157e+308, inf, -inf, nan, -nan)>
>>>
```

There is actually a function that can help visualize the binary
representation, it is a tuple that has 3 values that represent as
integers the sign, exponent and significand. This tuple is called tpl
and we can also see the respective binary representation:

```
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

The IEEE is a bit vage regarding the nans, there can be many more than
the 2 we've presented and the default base values can be
different. For this implementation and for the sake of simplicity,
only 2 are the accepted values for our Float64s eset.

### So what is the len?

As seen on the README file:

```
>>> len(f64s)
Traceback (most recent call last):
...
NotImplementedError: __len__ is limited use obj.len() instead
>>>
```

But we can use:

```
>>> f64s.len()
18437736874454810628
>>>
```

Using this we can calculate the number of bytes required to store
them, 64 bits are 8 bytes, so:

```
>>> f64s.len()*8
147501894995638485024
>>> f64s.len()*8//10**18 # Exabytes
147
>>> f64s.len()*8//2**60 # Exbibytes
127
>>>

```

So we need 147 exabites of a bit more precisely 127 exbibytes. A quick
comparison, a laptop hard drive has around 1TB, 1EB ~ 10**6 TB. So
around 100 million of these would be required to store all the 64 bit
floats.

### Yeah impressive, but wait that len is not 2**64

Yeah, that is actually:

```
>>> 2*(2**63-2**52+2) == 18437736874454810628
True
>>>
```

The Float64s eset is actually built on top a tpl version called
Float64_tpls:

```
>>> from esets import Float64_tpls
>>> f64tpls = Float64_tpls()
>>> f64tpls
<esets.Float64_tpls ((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1), ..., (0, 2047, 4503599627370495), (1, 2047, 4503599627370495))>
>>>
```

so we can simply get the index of the `-nan` plus one to get that
precise number too:

```
>>> f64tpls[:f64tpls.index((1, 2047, 1))+1].len()
18437736874454810628
>>>
```

### Ok back to the Float64s, what if I just want the positives

As in the case of the integers the floats are "folded" with
alternating positive and negative values, so we can extract them via a
simple slice with a step of two. Something similar can also be done
with the negatives but using the start as 1:

```
>>> pf64s = f64s[::2]
>>> pf64s
<esets.Float64s (0, 4.9406564584124654e-324, 9.8813129168249309e-324, 1.4821969375237396e-323, ..., inf, nan)>
>>> nf64s = f64s[1::2]
>>> nf64s
<esets.Float64s (-0, -4.9406564584124654e-324, -9.8813129168249309e-324, -1.4821969375237396e-323, ..., -inf, -nan)>
>>>
```

And as expected their lens are half of the total:

```
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

```
>>> 1.4 * pf64s[1] == pf64s[1]
True
>>>
```

That is a numer greater than zero (also that is not something weird
like an `inf` or a `nan`) multiplied by something greater than 1 is
the same number!

That doesn't happen with the Real numbers, on that case it doesn't
even make sense to even concieve the first number after zero. It just
doesn't exist. And if you would grab any Real number (exluding zero)
none would satisfy the above relationship. Also for any `n` say 1000,
the average of 2 consecutive positive floats satisfy:

```
>>> n = 1000
>>> (pf64s[n]+pf64s[n+1])/2 == pf64s[n]
True
>>>
```

Note that we are using the `==` which is normally a big no NO when
dealing with floats. But is is ok, we know what we are doing (I
think...).

We could look into more weirdness in how floats behave, but let's move
forward. The key takeaway is simply to note that they are in fact
incredibly useful but we need to be aware of their limitations. It
doesn't matter how many bits are used, they simply aren't continuous
and operating with them can lead to information loss. That isn't bad
for many intended purposes.

### But?

Yeah there is a but.

But for the case of enumerating rounding off stuff can give completely
different results. Granted floats aren't used for that normally, so
for all intended purposes we are safe.

Let's explore some other properties. An eset has the `__contains__`
method so we can use the `in` operation:

```
>>> 0.0 in pf64s
True
>>> 0.0 in pf64s[1:]
False
>>> -5 in pf64s
False
>>>
```

That ^ is kind of dumb I know but worth showing it also:

```
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

It maybe more clear seeing the following:

```
>>> 0.2 in pf64s # Still odd, I'll explain below
True
>>>
```

Let's print it with 17 digits to better explain:

```
>>> format(0.2, '.17g')
'0.20000000000000001'
>>>
```

Yep ^, 0.2 (a.k.a 1/5) cannot be properly represented in
binary. Python seems to be cheating here, our value is converted to a
float i.e. 0.2 turns into a 0.20000000000000001 and then it says yeah
that float value is present. This would happen on other programming
languajes by the way, that conversion is done under the hood and is
actually expected. But in this particular case we need to highlight
it, Real values are rounded to the nearest float. And on the
aforementioned `pi` approximation:

```
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

```
>>> from fractions import Fraction
>>> Fraction(1, 5) in pf64s
False
>>>
```

This way, we have avoided the float conversion and it clearly shows a
whole in the floats. Fractions are essentially Rational numbers, and
regarding the previous discussion of the Reals, yes the tag is more
appropriate.

Note index method is actually able to get the integer value of any float:

```
>>> pf64s.index(2.718281)
4613303443449361558
>>>
```

That number is an approximation of e. And for the positive floats,
that corresponds to the 4613303443449361558 positive float. The next
one is:

```
>>> pf64s[pf64s.index(2.718281)+1]
2.7182810000000006
>>>
```

We can simply get a slice starting from the first approximation:

```
>>> pf64s[pf64s.index(2.718281):]
<esets.Float64s (2.7182810000000002, 2.7182810000000006, 2.7182810000000011, 2.7182810000000015, ..., inf, nan)>
>>>
```

Also define the stop index to be the next number in the least
significant digit 2.718282 making, saving that eset into a variable
called sliver:

```
>>> sliver = pf64s[pf64s.index(2.718281):pf64s.index(2.718282)]
>>> sliver
<esets.Float64s (2.7182810000000002, 2.7182810000000006, 2.7182810000000011, 2.7182810000000015, ..., 2.718281999999999, 2.7182819999999994)>
>>>
```

We can even get the len:

```
>>> sliver.len()
2251799813
>>>
```

A lot of 64 bit floats on that "small" slice. Let's search for the
index on that sliver variable of the value of `e` directly from the
math library.

```
>>> from math import e
>>> e
2.718281828459045
>>> sliver.index(e)
1865523923
>>>
```

So as expected:

```
>>> sliver[1865523923]
2.718281828459045
>>>
```

### What about the epsilon?

That is actually straightforward we simply find the index of the 1.0
and add one to that index and then take the difference between the
pf64s float on that value and 1.0:

```
>>> pf64s[pf64s.index(1.0)+1]-1.0
2.220446049250313e-16
>>>
```

No need to do a while loop just a simple substraction once we have the
desired index. However, we can actually generalize quite easely to an
epsilon function defined on almost all the floats like the following:

```
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

Also, note the following:

```
>>> pf64s[-5:]
<esets.Float64s (1.7976931348623153e+308, 1.7976931348623155e+308, 1.7976931348623157e+308, inf, nan)>
>>>
```

The highest numeric value is 1.7976931348623155e+308

### Ok so that should be last possible integer it can contain, right?

Yes, but there are integer wholes there too.

### Where? How can they be found?

So the significand (the fractional part of the float64) has 52 bits,
 any number higher than this (2**52) cannot have a fractional part
 that is only integers:

```
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

```
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

This goes all the way until 2**53:

```
>>> pf64s[pf64s.index(2**52):pf64s.index(2**53)]
<esets.Float64s (4503599627370496, 4503599627370497, 4503599627370498, 4503599627370499, ..., 9007199254740990, 9007199254740991)>
>>>
```

Notice the lack of decimal values, actually:

```
>>> 4503599627370496.5 in  pf64s[pf64s.index(2**52):pf64s.index(2**53)]
True
>>> (Fraction(4503599627370496)+Fraction(1/2)) in  pf64s[pf64s.index(2**52):pf64s.index(2**53)]
False
>>>
```

Yep the internal float conversion can try to fool us again but the
Fractions come to the rescue.

### So the integer wholes are from 2**53 and on?

Exactly between 2**53 and 2**54 values start jumping in 2s:

```
>>> pf64s[pf64s.index(2**53):pf64s.index(2**54)]
<esets.Float64s (9007199254740992, 9007199254740994, 9007199254740996, 9007199254740998, ..., 18014398509481980, 18014398509481982)>
>>>
```

So:

```
>>> 9007199254740993 in pf64s[pf64s.index(2**53):pf64s.index(2**54)]
False
>>>
```

Also between 2**54 and 2**55 values start jumping in 4s:

```
>>> pf64s[pf64s.index(2**54):pf64s.index(2**55)]
<esets.Float64s (18014398509481984, 18014398509481988, 18014398509481992, 18014398509481996, ..., 36028797018963960, 36028797018963964)>
>>>
```

### Were do subnormals (a.k.a. denormals) fall here?

So the first subnormal (the exponent bits are zero) is zero and the
last has all ones on the significand that is 2**52-1, so looking and
the pf64s:

```
>>> pf64s.tpl2bintpl((0, 0, 2**52-1))
('0', '00000000000', '1111111111111111111111111111111111111111111111111111')
>>> pf64s[:pf64s.f64tpls.index((0, 0, 2**52-1))+1]
<esets.Float64s (0, 4.9406564584124654e-324, 9.8813129168249309e-324, 1.4821969375237396e-323, ..., 2.2250738585072004e-308, 2.2250738585072009e-308)>
>>>
```

The amount of positive subnormals are:

```
>>> pf64s[:pf64s.f64tpls.index((0, 0, 2**52-1))+1].len()
4503599627370496
>>>
```

And the total (including the negatives) is:

```
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()
9007199254740992
>>>
```

The total storage capacity to store these is:

```
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()//8//10**12 # Terabytes
1125
>>> f64s[:f64s.f64tpls.index((1, 0, 2**52-1))+1].len()//8//2**40 # Tebibytes
1024
>>>
```

So around 1000 of these laptop harddrives, more doable than the entire
64bit floats. But still kind of out of reach through conventional
approaches like using lists or tuples, but definetively reachable via
the Float64s eset B-).
