from math import factorial, comb, perm
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
        elif remaining_k > sum(rem):
            # Even every remaining class at full capacity can't reach
            # remaining_k: no need to branch to find that out.
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

    # The count is invariant under reordering the classes (it depends only
    # on the multiset of capacities, not their positions), but the
    # recursion's cost isn't: ascending order lets the "capacities can't
    # bind" shortcut above trigger as soon as only large-capacity classes
    # are left, instead of branching on them first.
    return count(tuple(sorted(multiplicities)), k)


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


def partitions_count(n: int, m: int) -> int:
    memo: dict[tuple[int, int], int] = {}

    def f(n: int, m: int) -> int:
        if m > n:
            m = n
        key = (n, m)
        if key in memo:
            return memo[key]
        if n == 0:
            result = 1
        elif m == 0:
            result = 0
        else:
            result = f(n, m - 1) + f(n - m, m)
        memo[key] = result
        return result

    return f(n, m)


def get_partition(val: int, n: int) -> tuple[int] | None:
    total = partitions_count(n, n)
    if val >= total or val < 0:
        return None

    def place(resval: int, n: int, m: int, retlist: list[int]) -> list[int]:
        if n == 0:
            return retlist
        return try_first(resval, n, m, retlist, 1)

    def try_first(
        resval: int, n: int, m: int, retlist: list[int], first: int
    ) -> list[int]:
        block = partitions_count(n - first, first)
        if resval < block:
            return place(resval, n - first, first, retlist + [first])
        return try_first(resval - block, n, m, retlist, first + 1)

    return tuple(place(val, n, n, []))


def get_partition_number(partition: tuple[int], n: int) -> int | None:
    if sum(partition) != n:
        return None
    if any(p <= 0 for p in partition):
        return None
    if list(partition) != sorted(partition, reverse=True):
        return None

    def rank(n: int, seq: list[int]) -> int:
        if not seq:
            return 0
        return locate(n, seq, 1)

    def locate(n: int, seq: list[int], candidate: int) -> int:
        block = partitions_count(n - candidate, candidate)
        if candidate == seq[0]:
            return rank(n - candidate, seq[1:])
        return block + locate(n, seq, candidate + 1)

    return rank(n, list(partition))


def get_arrangement(val: int, n: int, r: int) -> tuple[int] | None:
    total = perm(n, r)
    if val >= total or val < 0:
        return None

    def get_idx_list(resval: int, remaining_r: int, retlist: list[int]) -> list[int]:
        if remaining_r == 0:
            return retlist
        fact_val = perm(len(reslist) - 1, remaining_r - 1)
        div, mod = divmod(resval, fact_val)
        v = reslist.pop(div)
        retlist.append(v)
        return get_idx_list(mod, remaining_r - 1, retlist)

    reslist = list(range(n))
    return tuple(get_idx_list(val, r, []))


def get_arrangement_number(arrangement: tuple[int], n: int) -> int | None:
    r = len(arrangement)
    if len(set(arrangement)) != r or any(v < 0 or v >= n for v in arrangement):
        return None

    reslist = list(range(n))

    def get_number(arr: list[int], remaining_r: int) -> int:
        if remaining_r == 0:
            return 0
        fact_val = perm(len(reslist) - 1, remaining_r - 1)
        vi = reslist.index(arr[0])
        reslist.pop(vi)
        return fact_val * vi + get_number(arr[1:], remaining_r - 1)

    return get_number(list(arrangement), r)


def multiset_arrangement_count(multiplicities: tuple[int, ...], r: int) -> int:
    memo: dict[tuple[tuple[int, ...], int], int] = {}

    def g(rem: tuple[int, ...], remaining_r: int) -> int:
        key = (rem, remaining_r)
        if key in memo:
            return memo[key]
        if remaining_r == 0:
            result = 1
        elif not rem:
            result = 0
        elif remaining_r > sum(rem):
            # Even every remaining class at full capacity can't reach
            # remaining_r: no need to branch to find that out.
            result = 0
        elif remaining_r <= min(rem):
            # Capacities can't bind: every one of the remaining_r ordered
            # slots can freely pick any of the len(rem) remaining classes.
            result = len(rem) ** remaining_r
        else:
            # Choose x occurrences of the current class, choose which x of
            # the remaining_r open slots they take (comb), and recurse on
            # the rest with the later classes.
            result = sum(
                comb(remaining_r, x) * g(rem[1:], remaining_r - x)
                for x in range(min(rem[0], remaining_r) + 1)
            )
        memo[key] = result
        return result

    # See multiset_combination_count: the count doesn't depend on class
    # order, but ascending order lets the shortcut above trigger sooner.
    return g(tuple(sorted(multiplicities)), r)


def get_multiset_arrangement(
    val: int, multiplicities: tuple[int, ...], r: int
) -> tuple[int] | None:
    total = multiset_arrangement_count(multiplicities, r)
    if val >= total or val < 0:
        return None

    def place(
        resval: int,
        remaining_mult: tuple[int, ...],
        remaining_r: int,
        retlist: list[int],
    ) -> list[int]:
        if remaining_r == 0:
            return retlist
        candidates = [c for c in range(len(remaining_mult)) if remaining_mult[c] > 0]
        return try_candidate(resval, remaining_mult, remaining_r, retlist, candidates)

    def try_candidate(
        resval: int,
        remaining_mult: tuple[int, ...],
        remaining_r: int,
        retlist: list[int],
        candidates: list[int],
    ) -> list[int]:
        label = candidates[0]
        new_mult = list(remaining_mult)
        new_mult[label] -= 1
        rest_mult = tuple(new_mult)
        block = multiset_arrangement_count(rest_mult, remaining_r - 1)
        if resval < block:
            return place(resval, rest_mult, remaining_r - 1, retlist + [label])
        return try_candidate(
            resval - block, remaining_mult, remaining_r, retlist, candidates[1:]
        )

    return tuple(place(val, multiplicities, r, []))


def get_multiset_arrangement_number(
    arrangement: tuple[int, ...], multiplicities: tuple[int, ...]
) -> int | None:
    r = len(arrangement)
    counts = Counter(arrangement)
    if any(
        c < 0 or c >= len(multiplicities) or counts[c] > multiplicities[c]
        for c in counts
    ):
        return None

    def rank(remaining_mult: tuple[int, ...], remaining_r: int, seq: list[int]) -> int:
        if not seq:
            return 0
        candidates = [c for c in range(len(remaining_mult)) if remaining_mult[c] > 0]
        return locate(remaining_mult, remaining_r, seq, candidates)

    def locate(
        remaining_mult: tuple[int, ...],
        remaining_r: int,
        seq: list[int],
        candidates: list[int],
    ) -> int:
        label = candidates[0]
        new_mult = list(remaining_mult)
        new_mult[label] -= 1
        rest_mult = tuple(new_mult)
        block = multiset_arrangement_count(rest_mult, remaining_r - 1)
        if label == seq[0]:
            return rank(rest_mult, remaining_r - 1, seq[1:])
        return block + locate(remaining_mult, remaining_r, seq, candidates[1:])

    return rank(multiplicities, r, list(arrangement))


def get_subset(val: int, n: int) -> tuple[int] | None:
    total = 2**n
    if val >= total or val < 0:
        return None

    def try_size(resval: int, k: int) -> tuple[int]:
        block = comb(n, k)
        if resval < block:
            return get_combination(resval, n, k)
        return try_size(resval - block, k + 1)

    return try_size(val, 0)


def get_subset_number(subset: tuple[int], n: int) -> int | None:
    combo_rank = get_combination_number(subset, n)
    if combo_rank is None:
        return None

    def offset(size: int) -> int:
        if size == 0:
            return 0
        return comb(n, size - 1) + offset(size - 1)

    return offset(len(subset)) + combo_rank


def multiset_powerset_count(multiplicities: tuple[int, ...]) -> int:
    total = 1
    for count in multiplicities:
        total *= count + 1
    return total


def get_multiset_subset(val: int, multiplicities: tuple[int, ...]) -> tuple[int] | None:
    total = multiset_powerset_count(multiplicities)
    if val >= total or val < 0:
        return None

    def try_size(resval: int, k: int) -> tuple[int]:
        block = multiset_combination_count(multiplicities, k)
        if resval < block:
            return get_multiset_combination(resval, multiplicities, k)
        return try_size(resval - block, k + 1)

    return try_size(val, 0)


def get_multiset_subset_number(
    subset: tuple[int, ...], multiplicities: tuple[int, ...]
) -> int | None:
    combo_rank = get_multiset_combination_number(subset, multiplicities)
    if combo_rank is None:
        return None

    def offset(size: int) -> int:
        if size == 0:
            return 0
        return multiset_combination_count(multiplicities, size - 1) + offset(size - 1)

    return offset(len(subset)) + combo_rank


def is_valid_rgs(rgs: tuple[int, ...]) -> bool:
    """A restricted growth string: rgs[0] == 0, and each subsequent
    entry is at most one more than the running maximum so far. Block
    labels are introduced in order of first appearance, which is what
    makes this the standard bijective encoding of a set partition."""
    if not rgs:
        return True
    if rgs[0] != 0:
        return False
    running_max = 0
    for a in rgs[1:]:
        if a < 0 or a > running_max + 1:
            return False
        running_max = max(running_max, a)
    return True


def set_partition_count(r: int, m: int) -> int:
    """The number of ways to extend a restricted growth string with m
    blocks already established, for r more positions: at each of the r
    positions, join one of the m existing blocks, or start a new one
    (m+1 choices), recursing with the resulting block count."""
    memo: dict[tuple[int, int], int] = {}

    def T(r: int, m: int) -> int:
        key = (r, m)
        if key in memo:
            return memo[key]
        if r == 0:
            result = 1
        else:
            result = m * T(r - 1, m) + T(r - 1, m + 1)
        memo[key] = result
        return result

    return T(r, m)


def get_set_partition(val: int, n: int) -> tuple[int] | None:
    total = 1 if n == 0 else set_partition_count(n - 1, 1)
    if val >= total or val < 0:
        return None
    if n == 0:
        return ()

    def place(resval: int, remaining: int, m: int, retlist: list[int]) -> list[int]:
        if remaining == 0:
            return retlist
        return try_label(resval, remaining, m, retlist, 0)

    def try_label(
        resval: int, remaining: int, m: int, retlist: list[int], c: int
    ) -> list[int]:
        new_m = m + 1 if c == m else m
        block = set_partition_count(remaining - 1, new_m)
        if resval < block:
            return place(resval, remaining - 1, new_m, retlist + [c])
        return try_label(resval - block, remaining, m, retlist, c + 1)

    return tuple([0] + place(val, n - 1, 1, []))


def get_set_partition_number(rgs: tuple[int, ...]) -> int | None:
    if not is_valid_rgs(rgs):
        return None
    n = len(rgs)
    if n == 0:
        return 0

    def rank(seq: list[int], m: int) -> int:
        if not seq:
            return 0
        return locate(seq, m, 0)

    def locate(seq: list[int], m: int, c: int) -> int:
        new_m = m + 1 if c == m else m
        block = set_partition_count(len(seq) - 1, new_m)
        if seq[0] == c:
            return rank(seq[1:], new_m)
        return block + locate(seq, m, c + 1)

    return rank(list(rgs[1:]), 1)


def get_composition(val: int, n: int) -> tuple[int] | None:
    if n == 0:
        return () if val == 0 else None
    total = 2 ** (n - 1)
    if val >= total or val < 0:
        return None

    # A composition of n is a subset of the n-1 gaps between n items in a
    # row (which gaps get a divider), so this reuses get_subset directly,
    # applied to the complementary "no divider here" gaps -- chosen so
    # that composition #0 is (1, 1, ..., 1) and the last is (n,), the
    # same convention get_partition uses.
    no_divider_gaps = get_subset(val, n - 1)
    dividers = sorted(set(range(n - 1)) - set(no_divider_gaps))

    parts = []
    prev = 0
    for d in dividers:
        parts.append(d + 1 - prev)
        prev = d + 1
    parts.append(n - prev)
    return tuple(parts)


def get_composition_number(composition: tuple[int], n: int) -> int | None:
    if n == 0:
        return 0 if composition == () else None
    if sum(composition) != n or any(p <= 0 for p in composition):
        return None

    dividers = []
    running = 0
    for p in composition[:-1]:
        running += p
        dividers.append(running - 1)
    no_divider_gaps = tuple(sorted(set(range(n - 1)) - set(dividers)))
    return get_subset_number(no_divider_gaps, n - 1)


def derangement_count(n: int) -> int:
    """The subfactorial !n: permutations of range(n) with no fixed
    point, via the classic D(n) = (n-1)*(D(n-1)+D(n-2))."""
    memo: dict[int, int] = {}

    def D(n: int) -> int:
        if n in memo:
            return memo[n]
        if n == 0:
            result = 1
        elif n == 1:
            result = 0
        else:
            result = (n - 1) * (D(n - 1) + D(n - 2))
        memo[n] = result
        return result

    return D(n)


def get_derangement(val: int, n: int) -> tuple[int] | None:
    total = derangement_count(n)
    if val >= total or val < 0:
        return None

    # Classic derangement bijection: fix where the smallest remaining
    # label (a) maps to (candidate b), then split on what happens to b:
    #  - "close": b maps back to a (a 2-cycle), leaving a plain
    #    derangement of everyone else -- D(len(rest) - 2) ways.
    #  - "continue": b maps elsewhere. Build tau, an ordinary
    #    derangement of (remaining minus a) -- D(len(rest) - 1) ways --
    #    then recover the real assignment by redirecting whichever
    #    position tau sent to b so it goes to a instead (b's own image
    #    is used as-is; a derangement never has tau(b) == b, so exactly
    #    one other position redirects). This is the standard proof of
    #    D(n) = (n-1)*(D(n-1)+D(n-2)), turned into an unranking scheme.
    out: dict[int, int] = {}

    def place(resval: int, remaining: list[int], target: dict[int, int]) -> None:
        if not remaining:
            return
        a = remaining[0]
        try_candidate(resval, remaining, target, a, remaining[1:])

    def try_candidate(
        resval: int,
        remaining: list[int],
        target: dict[int, int],
        a: int,
        candidates: list[int],
    ) -> None:
        b = candidates[0]
        rest_without_a = [x for x in remaining if x != a]
        rest_without_ab = [x for x in rest_without_a if x != b]
        close_block = derangement_count(len(rest_without_ab))
        continue_block = derangement_count(len(rest_without_a))
        block = close_block + continue_block
        if resval < block:
            resolve(resval, target, a, b, rest_without_a, rest_without_ab, close_block)
            return
        try_candidate(resval - block, remaining, target, a, candidates[1:])

    def resolve(
        resval: int,
        target: dict[int, int],
        a: int,
        b: int,
        rest_without_a: list[int],
        rest_without_ab: list[int],
        close_block: int,
    ) -> None:
        if resval < close_block:
            target[a] = b
            target[b] = a
            place(resval, rest_without_ab, target)
            return
        resval -= close_block
        target[a] = b
        tau: dict[int, int] = {}
        place(resval, rest_without_a, tau)
        for x in rest_without_a:
            target[x] = a if tau[x] == b else tau[x]

    place(val, list(range(n)), out)
    return tuple(out[i] for i in range(n))


def get_derangement_number(perm: tuple[int], n: int) -> int | None:
    if sorted(perm) != list(range(n)) or any(perm[i] == i for i in range(n)):
        return None

    perm_dict = {i: perm[i] for i in range(n)}

    def rank(remaining: list[int], pdict: dict[int, int]) -> int:
        if not remaining:
            return 0
        a = remaining[0]
        return locate(remaining, pdict, a, pdict[a], remaining[1:])

    def locate(
        remaining: list[int],
        pdict: dict[int, int],
        a: int,
        b_actual: int,
        candidates: list[int],
    ) -> int:
        cand = candidates[0]
        rest_without_a = [x for x in remaining if x != a]
        rest_without_a_cand = [x for x in rest_without_a if x != cand]
        close_block = derangement_count(len(rest_without_a_cand))
        continue_block = derangement_count(len(rest_without_a))
        block = close_block + continue_block
        if cand == b_actual:
            if pdict[b_actual] == a:
                return rank(rest_without_a_cand, pdict)
            b = b_actual
            tau = {}
            for x in rest_without_a:
                if x == b:
                    tau[x] = pdict[x]
                else:
                    tau[x] = b if pdict[x] == a else pdict[x]
            return close_block + rank(rest_without_a, tau)
        return block + locate(remaining, pdict, a, b_actual, candidates[1:])

    return rank(list(range(n)), perm_dict)


def get_cartesian_index(val: int, sizes: tuple[int, ...]) -> tuple[int, ...] | None:
    total = 1
    for size in sizes:
        total *= size
    if val >= total or val < 0:
        return None

    # Standard mixed-radix decomposition, last source varying fastest
    # (the same order itertools.product uses): peel off the least
    # significant "digit" -- the last source's index -- first.
    result = []
    remaining = val
    for size in reversed(sizes):
        remaining, r = divmod(remaining, size)
        result.append(r)
    return tuple(reversed(result))


def get_cartesian_index_number(
    idx: tuple[int, ...], sizes: tuple[int, ...]
) -> int | None:
    if len(idx) != len(sizes):
        return None
    if any(i < 0 or i >= size for i, size in zip(idx, sizes)):
        return None

    val = 0
    for i, size in zip(idx, sizes):
        val = val * size + i
    return val
