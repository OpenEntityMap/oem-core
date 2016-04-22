from oem_core.models.collection import Collection
from oem_core.models.format import Format

import logging
import os

log = logging.getLogger(__name__)


class Database(object):
    def __init__(self, path, fmt, source, target):
        self.path = path
        self.format = fmt

        self.source = source
        self.target = target

        self.collections = {}

    @classmethod
    def load(cls, path, fmt, source, target):
        if not isinstance(fmt, Format):
            raise ValueError('Invalid value provided for the "fmt" parameter')

        # Construct database
        return cls(path, fmt, source, target)

    def load_collection(self, source, target):
        collection_path = os.path.join(self.path, source)

        # Open collection
        try:
            collection = Collection.load(collection_path, self.format, source, target)
        except Exception, ex:
            log.warn('Unable to load collection %r (format: %r) - %s', collection_path, self.format, ex, exc_info=True)
            return

        # Store collection
        self.collections[source] = collection

    def load_collections(self, collections=None):
        if collections is None:
            raise NotImplementedError

        for source, target in collections:
            # Load collection
            self.load_collection(source, target)

    def __repr__(self):
        return '<Database oem-%s-%s (%s)>' % (
            self.source,
            self.target,
            self.format.extension if self.format else None
        )
