from oem_framework.format import Format
from oem_framework.models.core import ModelRegistry
from oem_framework import models

import logging
import os

log = logging.getLogger(__name__)


class Database(models.Database):
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
            collection = ModelRegistry['Collection'].load(collection_path, self.format, source, target)
        except Exception, ex:
            log.warn('Unable to load collection %r (format: %r) - %s', collection_path, self.format, ex, exc_info=True)
            return None

        # Store collection
        self.collections[source] = collection
        return collection

    def load_collections(self, collections=None):
        if collections is None:
            raise NotImplementedError

        for source, target in collections:
            # Load collection
            self.load_collection(source, target)
