from eset import BEset


class BEvens(BEset):
    """A blind eset for evens"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.VALUE = 2

    def direct_function(self, i):
        return i * self.VALUE

    def stop_init(self):
        return None
