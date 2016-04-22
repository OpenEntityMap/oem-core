class BaseMapping(object):
    __slots__ = ['collection']

    def __init__(self, collection):
        self.collection = collection

    def to_dict(self, key=None):
        raise NotImplementedError
