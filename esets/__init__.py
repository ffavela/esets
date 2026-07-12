"""esets: lazy, index-addressable enumerated sets, including a full
combinatorics family (permutations, combinations, arrangements,
subsets, integer partitions, set partitions, derangements, and
Cartesian products), all randomly-accessible by index with no
enumeration of what comes before.

See README.md, COMBINATORICS.md, FLOAT64S.md, and POKER.md for the
full tour; this module just re-exports the public API in one place.
"""

from .eset import BEset, Eset, EMap, EABCMixinFactory
from .besets import BEvens, BWholesSHA256s

from .numeric import (
    Evens,
    Multiples,
    Negatives,
    Integers,
    Squares,
    Wholes,
    Float64_tpls,
    Float64s,
    Float64sMixin,
    IntArithProg,
)

from .cesets import (
    Natural_Permutator,
    Distinct_Permutator,
    Natural_Multiset_Permutator,
    Permutator,
    Natural_Combinator,
    Distinct_Combinator,
    Natural_Multiset_Combinator,
    Combinator,
    Natural_Arranger,
    Distinct_Arranger,
    Natural_Multiset_Arranger,
    Arranger,
    Natural_Powerset,
    Distinct_Powerset,
    Natural_Multiset_Powerset,
    Powerset,
    Partitioner,
    Compositioner,
    Natural_Set_Partitioner,
    Set_Partitioner,
    Natural_Derangement,
    Distinct_Derangement,
    Natural_Cartesian_Product,
    Cartesian_Product,
)

from . import ecombinatorics

__version__ = "0.1.0"

__all__ = [
    "BEset",
    "Eset",
    "EMap",
    "EABCMixinFactory",
    "BEvens",
    "BWholesSHA256s",
    "Evens",
    "Multiples",
    "Negatives",
    "Integers",
    "Squares",
    "Wholes",
    "Float64_tpls",
    "Float64s",
    "Float64sMixin",
    "IntArithProg",
    "Natural_Permutator",
    "Distinct_Permutator",
    "Natural_Multiset_Permutator",
    "Permutator",
    "Natural_Combinator",
    "Distinct_Combinator",
    "Natural_Multiset_Combinator",
    "Combinator",
    "Natural_Arranger",
    "Distinct_Arranger",
    "Natural_Multiset_Arranger",
    "Arranger",
    "Natural_Powerset",
    "Distinct_Powerset",
    "Natural_Multiset_Powerset",
    "Powerset",
    "Partitioner",
    "Compositioner",
    "Natural_Set_Partitioner",
    "Set_Partitioner",
    "Natural_Derangement",
    "Distinct_Derangement",
    "Natural_Cartesian_Product",
    "Cartesian_Product",
    "ecombinatorics",
]
