from oem_core.models.movie import Movie
from oem_core.models.show import Show


class Item(object):
    @classmethod
    def construct(cls, collection, media, **kwargs):
        if media == 'show':
            return Show(collection, **kwargs)

        if media == 'movie':
            return Movie(collection, **kwargs)

        raise Exception('Unknown media: %r' % media)

    @classmethod
    def parse(cls):
        pass
