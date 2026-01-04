from math import factorial


def get_permutation(val: int, size: int) -> tuple[int] | None:
    factorial_n = factorial(size)

    if val >= factorial_n or val < 0:
        return None

    def get_idx_list(resval: int, retlist: list[int]):
        if len(reslist) == 1:
            retlist.append(reslist[0])
            return retlist

        fact_val = factorial(len(reslist)-1)
        div, mod = divmod(resval, fact_val)

        val = reslist.pop(div)
        retlist.append(val)
        return get_idx_list(mod, retlist)

    reslist = list(range(size))
    return tuple(get_idx_list(val, []))
