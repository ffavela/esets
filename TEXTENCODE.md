# Alphabets from text: encoding a small file

`Arranger`, `Combinator`, and `Permutator` (see
[COMBINATORICS.md](COMBINATORICS.md)) address multiset combinatorics
by canonical class label, and nothing about that requires the classes
to be single characters -- an "alphabet" here is just a sequence of
unique, hashable values. This file takes that literally: it builds two
different alphabets out of the same short text, one character at a
time and one word at a time, and uses them to encode the text as a
single combinatorial index instead of as its own bytes.

This is a small-file demo on purpose. Generalizing it -- larger texts,
a fixed whole-language word alphabet shared across many documents,
chasing a real "compression ratio" -- is a deliberate follow-up, not
attempted here; the last section says exactly what stands in its way.

## Building an alphabet

An alphabet is nothing more than the distinct tokens a text breaks
into, in whatever order you want class `0` to mean:

```python
>>> tokens = ('a', 'b', 'a', 'c')
>>> alphabet = list(dict.fromkeys(tokens))
>>> alphabet
['a', 'b', 'c']

```

What "a token" *is* is entirely up to how the text gets split before
this point -- a single character, a whole word, or anything else
hashable. That choice is the real subject of this file.

An alphabet only says which classes exist; it says nothing about how
many of each there are, which is exactly what a capacities (or
multiplicities) tuple needs. `Counter` is the bridge between the two
-- count the tokens, then read off one number per alphabet class, in
the alphabet's own order:

```python
>>> from collections import Counter
>>> counts = Counter(tokens)
>>> tuple(counts[c] for c in alphabet)
(2, 1, 1)

```

`(2, 1, 1)` -- two `'a'`s, one `'b'`, one `'c'` -- is precisely the
multiplicities tuple `Natural_Multiset_Arranger`, `Natural_Multiset_Combinator`,
and `Natural_Multiset_Permutator` take directly, and it's exactly what
`Arranger`/`Combinator`/`Permutator` compute for you internally, via
`Counter(elements)`, whenever capacities aren't passed in explicitly.
This file builds that same tuple by hand a few times below instead of
leaving it hidden inside the wrapper -- and, later on, deliberately
*doesn't* build it that way once, which is worth being able to spot.

## An alphabet's order is a choice, not a fact

Everything downstream -- `Arranger`, `Combinator`, `Permutator`, and
the word "lexicographic" used later in this file -- ranks tokens by
comparing their positions in `alphabet`, low to high. It's easy to
misread that as "alphabetical order," the A-before-B-before-C one
learned in grade school. It isn't. It's "the order of whatever
sequence got passed in as `alphabet`" -- and that sequence can list
its entries in any order at all, as long as each is unique. There is
no "real" order underneath waiting to be respected; there's only
whichever one was supplied.

```python
>>> from esets.cesets import Arranger
>>> weird_alphabet = ['z', 'a', 'm']
>>> A = Arranger(('z', 'a', 'm'), 2, weird_alphabet)
>>> list(A)
[('z', 'a'), ('z', 'm'), ('a', 'z'), ('a', 'm'), ('m', 'z'), ('m', 'a')]

```

Every `z`-first pair comes before every `a`-first pair, which comes
before every `m`-first pair -- backwards from the everyday alphabet,
forwards from `weird_alphabet`. Nothing downstream (counting, ranking,
`.index()`, reconstruction) cares that this doesn't match the
dictionary; the only requirement is using the same `alphabet`
consistently for encoding and decoding, not matching some external
convention. The two alphabets built next in this file make the same
point with real data instead of a toy one: `char_alphabet` reaches for
`sorted()`, and `word_alphabet` reaches for something else entirely --
neither is "the" order, both are just choices, made explicit below
rather than left implicit.

## The sample text

Two lines of a public-domain tongue twister, chosen for its heavy
letter and word repetition -- exactly the shape that makes capped
multiset combinatorics pay off, versus a low-repetition string where
nothing repeats and there is nothing to compress:

```python
>>> text = (
...     "Peter Piper picked a peck of pickled peppers.\n"
...     "A peck of pickled peppers Peter Piper picked.\n"
... )
>>> len(text)
92

```

## Character-level tokenizing

The simplest split there is -- every character is its own token,
spaces, punctuation, and the newline included:

```python
>>> char_tokens = tuple(text)
>>> char_alphabet = sorted(set(char_tokens))
>>> char_alphabet
['\n', ' ', '.', 'A', 'P', 'a', 'c', 'd', 'e', 'f', 'i', 'k', 'l', 'o', 'p', 'r', 's', 't']
>>> len(char_alphabet)
18

```

`sorted()` here is doing the same job `weird_alphabet` did above,
just with a less startling result: for plain ASCII letters it happens
to land on ordinary A-Z order, which reads as "the" order only because
it's a familiar convenient choice, not because anything required it.

Nothing is discarded, so `''.join(char_tokens) == text` trivially --
reconstruction is exact by construction, before any encoding even
happens. The capacities behind that reconstruction are just `Counter`
again, one count per class in `char_alphabet`'s own order:

```python
>>> char_counts = Counter(char_tokens)
>>> char_capacities = tuple(char_counts[c] for c in char_alphabet)
>>> char_capacities
(2, 14, 2, 1, 4, 1, 6, 4, 16, 2, 6, 6, 2, 2, 14, 6, 2, 2)
>>> sum(char_capacities) == len(char_tokens)
True

```

That's not a separate fact from what `Arranger` does below -- it's
the same tuple `Arranger(char_tokens, ..., char_alphabet)` builds for
itself internally:

```python
>>> from esets.cesets import Arranger, Natural_Multiset_Arranger
>>> Natural_Multiset_Arranger(char_capacities, len(char_tokens)).len() == Arranger(char_tokens, len(char_tokens), char_alphabet).len()
True

```

## Word-level tokenizing, and what happens to spaces and punctuation

Splitting on whitespace (`text.split()`) is tempting and wrong in a
specific, demonstrable way -- punctuation rides along with the word it
touches, so the *same* word in two different positions can land in two
different token classes:

```python
>>> naive = text.split()
>>> Counter(naive)['peppers']
1
>>> Counter(naive)['peppers.']
1

```

"peppers" was said twice in this text. `text.split()` sees it as two
unrelated words that each happened once -- exactly backwards, since
recognizing the repeat is the entire point of using a multiset in the
first place. A regex that peels punctuation and whitespace runs off
into their own tokens keeps every repeat visible instead:

```python
>>> import re
>>> word_tokens = tuple(re.findall(r"\w+|[^\w\s]|\s+", text))
>>> ''.join(word_tokens) == text
True
>>> Counter(word_tokens)['peppers']
2
>>> word_alphabet = list(dict.fromkeys(word_tokens))
>>> word_alphabet
['Peter', ' ', 'Piper', 'picked', 'a', 'peck', 'of', 'pickled', 'peppers', '.', '\n', 'A']
>>> len(word_alphabet)
12
>>> word_capacities = tuple(Counter(word_tokens)[c] for c in word_alphabet)
>>> word_capacities
(2, 14, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1)
>>> sum(word_capacities) == len(word_tokens)
True

```

Same construction as `char_capacities` above, same `Counter`, just
counting a different kind of token -- `'peppers'` shows up as `2` here
for the same reason it showed up as `2` a moment ago, because this
tokenizer (unlike `text.split()`) keeps it as one class.

`word_alphabet` makes a different choice than `char_alphabet` did --
first-appearance order instead of `sorted()` -- and reads that way:
`'Peter'` is class 0 because it's the first token in the text, not
because it precedes `'Piper'` in a dictionary. Both are just
conventions; `sorted()` would have worked here too, and would have
produced a different (still perfectly valid) set of indices throughout
the rest of this file.

Lossless (`''.join` reconstructs `text` exactly, spaces/punctuation/
newlines included -- they're just tokens like any other, not discarded
and not special-cased) and, unlike the naive split, it doesn't fracture
a repeated word across its punctuation variants. Note that case is
left alone: "Peter" and "peter" would land in different classes if
this text used both -- folding case would shrink the alphabet further,
at the cost of losing which spelling was actually written. Not done
here, so the whole thing stays exactly reversible.

## Arranger: the text as one index

`Arranger(elements, r, alphabet)` with `r == len(elements)` encodes
the *entire* token stream as a single index into "every way to arrange
this exact multiset of tokens":

```python
>>> from esets.cesets import Arranger, Permutator
>>> A_char = Arranger(char_tokens, len(char_tokens), char_alphabet)
>>> char_idx = A_char.index(char_tokens)
>>> A_char[char_idx] == char_tokens
True
>>> char_idx.bit_length()
299

>>> A_word = Arranger(word_tokens, len(word_tokens), word_alphabet)
>>> word_idx = A_word.index(word_tokens)
>>> A_word[word_idx] == word_tokens
True
>>> word_idx.bit_length()
77

>>> round(char_idx.bit_length() / word_idx.bit_length(), 2)
3.88

```

Both round-trip exactly, and both need their own small header (the
histogram, i.e. which classes and how many of each -- 18 numbers for
the character alphabet, 12 for the word one) alongside the index to
mean anything. But the index itself is far smaller for the word-level
encoding -- 222 fewer bits for the same text, `char_idx.bit_length() -
word_idx.bit_length() == 222`, a **3.88x** ratio (the word-level index
needs roughly a quarter as many bits) -- because each *word* token
carries far more redundancy for the multiset to exploit than each
character does.

Be precise about what that `3.88x` is and isn't measuring, though: it
compares the two *indices* to each other, nothing else. It doesn't
include either header (the 18 or 12 numbers above), and it doesn't
compare either encoding against the size of `text` itself as a
baseline -- so it isn't a real, end-to-end compression ratio, just a
same-text, index-to-index one. That fuller accounting is exactly the
kind of thing the intro defers to a follow-up rather than attempting
here. What this number does show honestly: the gap between the two is
the whole motivation for eventually wanting a whole-language word
alphabet instead of a 12-word one built from a single sample -- the
more text a shared alphabet has seen, the more of its repetition an
arrangement index can absorb instead of paying for verbatim.

One more fact worth checking rather than assuming: when `r` equals the
full token count and every class's capacity is exactly its actual
count (nothing loose about it), `Arranger` and `Permutator` describe
the identical space -- forcing every slot to be filled leaves no room
for `Arranger`'s extra freedom to matter:

```python
>>> P_word = Permutator(word_tokens, word_alphabet)
>>> A_word.len() == P_word.len()
True
>>> A_word[0] == P_word[0]
True

```

## Combinator, then Permutator: what Arranger is doing conceptually

`Arranger`'s own docstring describes it as "the object you'd get by
taking a `Combinator` (choosing which r elements, content only) and,
for each of its results, running a `Permutator` over that specific
selection" -- computed directly instead of via that composition, for
speed. Building the composition by hand only becomes a nontrivial
exercise once the capacities are *looser* than what's actually used --
otherwise there is exactly one valid combination (using everything),
same as the identity just above. So here every class gets a generous,
shared capacity bound instead of its exact count, and only the first
8 tokens of the stream are addressed, so `Combinator` has real work to
do (which histogram is it) before `Permutator` decides the order:

```python
>>> from esets.cesets import Natural_Multiset_Arranger, Natural_Multiset_Combinator
>>> classes = word_alphabet
>>> labels = tuple(classes.index(t) for t in word_tokens)
>>> r = 8
>>> sl = labels[:r]
>>> sl_tokens = word_tokens[:r]
>>> sl_tokens
('Peter', ' ', 'Piper', ' ', 'picked', ' ', 'a', ' ')
>>> loose_capacities = tuple(len(word_tokens) for _ in classes)
>>> C = Natural_Multiset_Combinator(loose_capacities, r)
>>> C.len()
75582
>>> combo = tuple(sorted(sl))
>>> combo_idx = C.index(combo)
>>> combo_idx
12453

```

Notice `loose_capacities` isn't built with `Counter`, unlike
`char_capacities`/`word_capacities` earlier -- that's the deliberate
exception flagged back in "Building an alphabet." `Counter` gives the
*exact* histogram of what's actually there, which is exactly wrong
for this section: with exact counts and `r` equal to their sum, there
is only one valid combination (use everything), so `Combinator` would
have nothing to choose between and this whole composition would
collapse back to the trivial case already covered by the `Arranger`/
`Permutator` identity above. A capacity bound *looser* than reality --
here, just "as many as the whole token stream, per class," picked for
convenience rather than derived from anything -- is what gives
`Combinator` a real space of alternatives to rank `combo` against.

`combo_idx` alone only says *which 8-token multiset* this is, out of
75582 possible ones under these loose capacities -- not what order it
was in. `Permutator`, built fresh on just that specific multiset,
supplies the second half:

```python
>>> P = Permutator(sl_tokens, sorted(set(sl_tokens)))
>>> P.len()
1680
>>> perm_idx = P.index(sl_tokens)
>>> perm_idx
910

```

Reconstruction runs the same two steps in reverse -- `Combinator`
gives back the histogram, `Permutator` (rebuilt on that specific
histogram) gives back the order:

```python
>>> combo_reconstructed = C[combo_idx]
>>> histogram_tokens = sorted(classes[label] for label in combo_reconstructed)
>>> P_reconstruct = Permutator(histogram_tokens, sorted(set(histogram_tokens)))
>>> P_reconstruct[perm_idx] == sl_tokens
True

```

`(combo_idx, perm_idx)` and `Arranger`'s own single index for this
same slice cover the identical space, but there's no formula that
turns one into the other -- not because the arithmetic is subtle, but
because the two are built by walking the space in structurally
different orders. Flattening `Combinator` then `Permutator` puts every
arrangement of a given combination into one contiguous block, by
definition -- that's what "first pick which combination, then pick
which order within it" means. `Arranger` doesn't do that: it ranks by
raw lexicographic order across label positions (smallest feasible
label at position 0, then position 1, and so on -- see
`get_multiset_arrangement_number` in `esets/ecombinatorics.py`), which
interleaves arrangements from *different* combinations instead of
grouping them. A minimal example makes this concrete: 3 classes,
capacity 1 each, choosing 2 -- small enough to print in full:

```python
>>> tiny = Natural_Multiset_Arranger((1, 1, 1), 2)
>>> arranger_order = tuple(tiny[i] for i in range(tiny.len()))
>>> arranger_order
((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))

```

That's the `Arranger` side, in full. The `Combinator` side of the same
space -- 3 classes, capacity 1 each, choosing 2 -- is smaller: there
are only 3 distinct *combinations*, since order doesn't count here,
`(1, 0)` and `(0, 1)` are the same combination:

```python
>>> tiny_combos_obj = Natural_Multiset_Combinator((1, 1, 1), 2)
>>> tiny_combos = [tiny_combos_obj[i] for i in range(tiny_combos_obj.len())]
>>> tiny_combos
[(0, 1), (0, 2), (1, 2)]

```

Three combinations, canonical (non-decreasing) order, `Combinator`
index `0`, `1`, `2` respectively. Each one, on its own, is small enough
for its own `Permutator` to enumerate directly -- and since every
class here has capacity 1, each combination's 2 elements are always
distinct, so each block is the same size, 2:

```python
>>> blocks = [(combo, tuple(Permutator(combo))) for combo in tiny_combos]
>>> for combo, perms in blocks:
...     print(combo, '->', perms)
...
(0, 1) -> ((0, 1), (1, 0))
(0, 2) -> ((0, 2), (2, 0))
(1, 2) -> ((1, 2), (2, 1))

```

Flattening those three blocks in `Combinator`'s own order -- exactly
what "first pick which combination, then pick which order within it"
means, done by hand instead of via a formula -- produces a full
ordering of the same 6 arrangements `Arranger` enumerated above, but
grouped instead of interleaved:

```python
>>> grouped_order = tuple(p for combo, perms in blocks for p in perms)
>>> grouped_order
((0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1))
>>> grouped_order == arranger_order
False
>>> sorted(grouped_order) == sorted(arranger_order)
True

```

Same 6 arrangements either way (`sorted(...)` agrees), but a different
order (`==` doesn't). `grouped_order` keeps combination `(0, 1)`'s two
arrangements adjacent, positions 0 and 1; `arranger_order` splits them
across positions 0 and 2, with a `(0, 2)` arrangement in between at
position 1 -- `Arranger`'s raw lexicographic walk never grouped them
in the first place, so there was never a combination-sized block for
`Combinator`+`Permutator`'s construction to land back on. Both
orderings are valid, complete, and correct; they're just different
orderings of the same set, the same way "alphabetical" and "by length"
are both valid ways to sort the same list of words without one being
derivable from the other by a formula.

## Where this stops here, on purpose

Two things stand between this and a real "encode any file with a
language's whole vocabulary" tool, and neither is attempted in this
file:

* **Alphabet size.** `COMBINATORICS.md` already documents that the
  plain counting recursion "hits Python's recursion limit somewhere
  around 250-300 classes", and `COMBINATORIALDB.md` found ranking --
  exactly what every `.index()` call in this file is doing -- hits
  that wall sooner, since it has none of counting's shortcuts. A
  12-word or 18-character alphabet is nowhere near that ceiling; a
  real language's vocabulary (tens of thousands of words) is well past
  it. Getting there needs the ranking recursion fixed the way counting
  eventually was -- a different recursion with its own shape, not a
  corollary of the counting fixes, and not done here.
* **Text size.** `r` (and the capacities behind it) grew only to the
  length of two short lines here. Nothing in this file's approach
  changes conceptually for a longer text, but a genuinely large `r`
  needs the same ranking-side work as the alphabet-size problem above
  before it's practical, not just a bigger sample.

Both are real, scoped engineering, not open questions about whether
the approach works -- this file already shows that it does, end to
end, round-tripping exactly, on a text small enough to stay well clear
of either limit.
