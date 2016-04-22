from oem_core.models.base import BaseMedia


class Movie(BaseMedia):
    __slots__ = ['names', 'mappings']
    __attributes__ = ['names', 'mappings']

    def __init__(self, collection, identifiers, names, mappings=None, **kwargs):
        super(Movie, self).__init__(collection, 'movie', identifiers, **kwargs)

        self.names = names or set()

        self.mappings = mappings or []

    def add(self, item, service):
        # TODO manage movie duplicates
        pass
