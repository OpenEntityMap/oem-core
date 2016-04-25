from oem_core.models.base.writable import Writable
from oem_core.models.movie import Movie
from oem_core.models.show import Show


class Item(Writable):
    @classmethod
    def construct(cls, collection, media, **kwargs):
        if media == 'show':
            return Show(collection, **kwargs)

        if media == 'movie':
            return Movie(collection, **kwargs)

        raise ValueError('Unknown media: %r' % media)

    @classmethod
    def parse(cls, collection, data, media=None):
        if media is None:
            raise ValueError('Missing required parameter: "media"')

        if media == 'show':
            return Show.parse(collection, data)

        if media == 'movie':
            return Movie.parse(collection, data)

        raise ValueError('Unknown media: %r' % media)
