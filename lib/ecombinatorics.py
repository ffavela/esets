from math import factorial


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
