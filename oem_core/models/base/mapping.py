from oem_core.models.base.writable import Writable


class BaseMapping(Writable):
    __slots__ = ['collection']

    def __init__(self, collection):
        super(BaseMapping, self).__init__()

        self.collection = collection

    def to_dict(self, key=None):
        raise NotImplementedError
