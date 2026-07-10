from math import factorial, comb
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


def get_combination(val: int, n: int, k: int) -> tuple[int] | None:
    total = comb(n, k)
    if val >= total or val < 0:
        return None

    def place(resval: int, reslist: list[int], k: int, retlist: list[int]) -> list[int]:
        if k == 0:
            return retlist
        return try_candidate(resval, reslist, k, retlist)

    def try_candidate(
        resval: int, reslist: list[int], k: int, retlist: list[int]
    ) -> list[int]:
        candidate = reslist[0]
        rest = reslist[1:]
        block = comb(len(rest), k - 1)
        if resval < block:
            return place(resval, rest, k - 1, retlist + [candidate])
        return try_candidate(resval - block, rest, k, retlist)

    return tuple(place(val, list(range(n)), k, []))


def get_combination_number(combination: tuple[int], n: int) -> int | None:
    k = len(combination)
    if list(combination) != sorted(set(combination)):
        return None
    if combination and (combination[0] < 0 or combination[-1] >= n):
        return None

    def rank(reslist: list[int], seq: list[int]) -> int:
        if not seq:
            return 0
        return locate(reslist, seq)

    def locate(reslist: list[int], seq: list[int]) -> int:
        candidate = reslist[0]
        rest = reslist[1:]
        block = comb(len(rest), len(seq) - 1)
        if candidate == seq[0]:
            return rank(rest, seq[1:])
        return block + locate(rest, seq)

    return rank(list(range(n)), list(combination))


def multiset_combination_count(multiplicities: tuple[int, ...], k: int) -> int:
    memo: dict[tuple[tuple[int, ...], int], int] = {}

    def count(rem: tuple[int, ...], remaining_k: int) -> int:
        key = (rem, remaining_k)
        if key in memo:
            return memo[key]
        if remaining_k == 0:
            result = 1
        elif not rem:
            result = 0
        elif remaining_k <= min(rem):
            # Capacities can't bind: plain stars-and-bars (mset's C1 shortcut).
            result = comb(len(rem) + remaining_k - 1, remaining_k)
        else:
            result = sum(
                count(rem[1:], remaining_k - t)
                for t in range(min(rem[0], remaining_k) + 1)
            )
        memo[key] = result
        return result

    return count(multiplicities, k)


def get_multiset_combination(
    val: int, multiplicities: tuple[int, ...], k: int
) -> tuple[int] | None:
    total = multiset_combination_count(multiplicities, k)
    if val >= total or val < 0:
        return None

    def place(
        resval: int,
        classes: tuple[int, ...],
        remaining_k: int,
        class_id: int,
        retlist: list[int],
    ) -> list[int]:
        if remaining_k == 0:
            return retlist
        return try_count(
            resval,
            classes,
            remaining_k,
            class_id,
            retlist,
            min(classes[0], remaining_k),
        )

    def try_count(
        resval: int,
        classes: tuple[int, ...],
        remaining_k: int,
        class_id: int,
        retlist: list[int],
        t: int,
    ) -> list[int]:
        block = multiset_combination_count(classes[1:], remaining_k - t)
        if resval < block:
            return place(
                resval,
                classes[1:],
                remaining_k - t,
                class_id + 1,
                retlist + [class_id] * t,
            )
        return try_count(resval - block, classes, remaining_k, class_id, retlist, t - 1)

    return tuple(place(val, multiplicities, k, 0, []))


def get_multiset_combination_number(
    combination: tuple[int, ...], multiplicities: tuple[int, ...]
) -> int | None:
    if list(combination) != sorted(combination):
        return None
    counts = Counter(combination)
    if any(
        c < 0 or c >= len(multiplicities) or counts[c] > multiplicities[c]
        for c in counts
    ):
        return None

    def rank(
        classes: tuple[int, ...], remaining_k: int, class_id: int, seq: list[int]
    ) -> int:
        if remaining_k == 0:
            return 0
        actual = 0
        while actual < len(seq) and seq[actual] == class_id:
            actual += 1
        return locate(
            classes, remaining_k, class_id, seq, min(classes[0], remaining_k), actual
        )

    def locate(
        classes: tuple[int, ...],
        remaining_k: int,
        class_id: int,
        seq: list[int],
        t: int,
        actual: int,
    ) -> int:
        block = multiset_combination_count(classes[1:], remaining_k - t)
        if t == actual:
            return rank(classes[1:], remaining_k - t, class_id + 1, seq[t:])
        return block + locate(classes, remaining_k, class_id, seq, t - 1, actual)

    return rank(multiplicities, len(combination), 0, list(combination))
