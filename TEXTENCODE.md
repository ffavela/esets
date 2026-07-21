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

Nothing is discarded, so `''.join(char_tokens) == text` trivially --
reconstruction is exact by construction, before any encoding even
happens.

## Word-level tokenizing, and what happens to spaces and punctuation

Splitting on whitespace (`text.split()`) is tempting and wrong in a
specific, demonstrable way -- punctuation rides along with the word it
touches, so the *same* word in two different positions can land in two
different token classes:

```python
>>> naive = text.split()
>>> from collections import Counter
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

```

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

```

Both round-trip exactly, and both need their own small header (the
histogram, i.e. which classes and how many of each -- 18 numbers for
the character alphabet, 12 for the word one) alongside the index to
mean anything. But the index itself is far smaller for the word-level
encoding -- 222 fewer bits for the same text, `char_idx.bit_length() -
word_idx.bit_length() == 222` -- because each *word* token carries far
more redundancy for the multiset to exploit than each character does.
That gap is the whole motivation for eventually wanting a
whole-language word alphabet instead of a 12-word one built from a
single sample: the more text a shared alphabet has seen, the more of
its repetition an arrangement index can absorb instead of paying for
verbatim.

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
same slice cover the identical space -- but they are not the same
number, and not related by any simple formula. `Arranger` isn't
secretly running this composition internally; it ranks position by
position in one pass (see `get_multiset_arrangement_number` in
`esets/ecombinatorics.py`), a different bijection over the same set:

```python
>>> A_direct = Natural_Multiset_Arranger(loose_capacities, r)
>>> arranger_idx = A_direct.index(sl)
>>> arranger_idx
3509761
>>> combo_idx * P.len() + perm_idx == arranger_idx
False

```

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
