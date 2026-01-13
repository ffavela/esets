from eset import Eset
from lib.combinatorics import *
from math import factorial

class canonical_permutator(Eset):
    """A basic eset that handles permutations without repetition"""
    def direct_function(self, i):
        return self.get_permutation(i)

    def inverse_fun(self, val):
        return self.get_permutation_number(val)

    def stop_init(self, stop): # Maybe review this in the ABC...
        return factorial(stop)
