from oem_core.models.base import Writable


class Range(Writable):
    __slots__ = ['collection', 'start', 'end']

    def __init__(self, collection, start=0, end=100):
        super(Range, self).__init__()

        self.collection = collection

        self.start = start
        self.end = end

    def is_defined(self):
        return self.start != 0 or self.end != 100

    @classmethod
    def parse(cls, collection, data, **kwargs):
        return cls(
            collection,

            start=data.get('start', 0),
            end=data.get('end', 100)
        )

    def to_dict(self):
        result = {}

        if self.start != 0:
            result['start'] = self.start

        if self.end != 100:
            result['end'] = self.end

        return result
