from .eset import BEset
import hashlib


class BEvens(BEset):
    """A blind eset for evens"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.VALUE = 2

    def direct_function(self, i):
        return i * self.VALUE

    def stop_init(self):
        return None


class BWholesSHA256s(BEset):
    """A blind eset of SHA256s of the Whole numbers. It uses ascii encoding since only decimal numbers are expected."""

    def direct_function(self, i):
        return hashlib.sha256(str(i).encode('ascii')).hexdigest()

    def stop_init(self):
        return None
