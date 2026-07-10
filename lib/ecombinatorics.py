from math import factorial
from collections import Counter


def get_permutation(val: int, size: int) -> tuple[int] | None:
    factorial_n = factorial(size)

    if val >= factorial_n or val < 0:
        return None

    def get_idx_list(resval: int, retlist: list[int]):
        if len(reslist) <= 1:
            retlist.extend(reslist)
            return retlist

        fact_val = factorial(len(reslist) - 1)
        div, mod = divmod(resval, fact_val)

        val = reslist.pop(div)
        retlist.append(val)
        return get_idx_list(mod, retlist)

    reslist = list(range(size))
    return tuple(get_idx_list(val, []))


def get_permutation_number(nat_perm: tuple[int]) -> int | None:
    size = len(nat_perm)

    reslist = list(range(size))

    if sorted(nat_perm) != reslist:
        return None

    def get_number(perm):
        if len(perm) <= 1:
            return 0

        fnum = factorial(len(perm) - 1)
        val = reslist.index(perm[0])
        reslist.pop(val)

        return fnum * val + get_number(perm[1:])

    return get_number(nat_perm)


def multinomial(counts: dict[int, int]) -> int:
    n = sum(counts.values())
    denom = 1
    for c in counts.values():
        denom *= factorial(c)
    return factorial(n) // denom


def is_canonical_labels(labels: tuple[int]) -> bool:
    distinct = sorted(set(labels))
    return distinct == list(range(len(distinct)))


def get_multiset_permutation(val: int, labels: tuple[int]) -> tuple[int] | None:
    if not is_canonical_labels(labels):
        return None

    total = multinomial(Counter(labels))
    if val >= total or val < 0:
        return None

    def place(resval: int, reslist: list[int], retlist: list[int]) -> list[int]:
        if not reslist:
            return retlist
        return try_candidate(resval, reslist, retlist, list(dict.fromkeys(reslist)))

    def try_candidate(
        resval: int, reslist: list[int], retlist: list[int], candidates: list[int]
    ) -> list[int]:
        label = candidates[0]
        rest = reslist.copy()
        rest.remove(label)
        block = multinomial(Counter(rest))
        if resval < block:
            return place(resval, rest, retlist + [label])
        return try_candidate(resval - block, reslist, retlist, candidates[1:])

    return tuple(place(val, list(labels), []))


def get_multiset_permutation_number(perm: tuple[int], labels: tuple[int]) -> int | None:
    if not is_canonical_labels(labels):
        return None
    if Counter(perm) != Counter(labels):
        return None

    def rank(remaining: list[int], seq: list[int]) -> int:
        if not seq:
            return 0
        return locate(remaining, seq, list(dict.fromkeys(remaining)))

    def locate(remaining: list[int], seq: list[int], candidates: list[int]) -> int:
        label = candidates[0]
        rest = remaining.copy()
        rest.remove(label)
        if label == seq[0]:
            return rank(rest, seq[1:])
        return multinomial(Counter(rest)) + locate(remaining, seq, candidates[1:])

    return rank(list(labels), list(perm))
