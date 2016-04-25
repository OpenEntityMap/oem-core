from oem_core.models.format import Format
from oem_core.models.index import Index

import logging
import os

log = logging.getLogger(__name__)


class Collection(object):
    def __init__(self, path, source, target, fmt, index=None, minify=None):
        self.path = path
        self.source = source
        self.target = target

        self.format = fmt
        self.index = index

        self.minify = minify

    def get(self, key, hash=None, default=None):
        # Retrieve item
        item = self.index.get(key)

        if not item:
            return default

        # Match item (if `hash` provided)
        if hash is not None and item.hash != hash:
            return default

        return item

    def has(self, service, key, hash=None):
        return self.get(service, key, hash) is not None

    def set(self, key, metadata):
        if key is None:
            raise ValueError('Missing required parameter "key"')

        self.index[key] = metadata

    def write(self):
        # Write indices to disk
        if not self.index.write(fmt=self.format):
            log.warn('Unable to write index %r to disk', self.index)
            return False

        # Indices written to disk successfully
        return True

    @classmethod
    def load(cls, path, fmt, source=None, target=None):
        """Load collection from `path`

        :param path: Path to collection directory
        :type path: str

        :param fmt: Collection format
        :type fmt: Format

        :param source: Name of source service
        :type source: str

        :param target: Name of target service
        :type target: str

        :rtype: Collection
        """

        if not isinstance(fmt, Format):
            raise ValueError('Invalid value provided for the "fmt" parameter')

        # Construct collection
        collection = cls(path, source, target, fmt)

        # Open index
        collection.index = Index.load(collection, os.path.join(path, 'index.%s' % fmt.extension), fmt)

        # Construct collection
        return collection

    def __getitem__(self, key):
        return self.index[key]

    def __setitem__(self, key, value):
        self.index[key] = value

    def __repr__(self):
        if self.source and self.target:
            return '<Collection %s -> %s (%s)>' % (
                self.source,
                self.target,
                self.format.extension if self.format else None
            )

        return '<Collection %s (%s)>' % (
            self.source or self.target,
            self.format.extension if self.format else None
        )
