from oem_core.models.metadata import Metadata
from oem_core.models.writable import Writable

import json
import msgpack
import os


class Index(Writable):
    def __init__(self, collection, path, fmt, items=None):
        super(Index, self).__init__(path)

        self.collection = collection

        self.format = fmt
        self.items = items or {}

        # Build storage path
        self.item_path = os.path.join(os.path.dirname(path), 'items')

    def to_dict(self):
        return dict([
            (key, item.to_dict())
            for key, item in self.items.items()
        ])

    def get(self, key, default=None):
        return self.items.get(key, default)

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value

    @classmethod
    def load(cls, collection, path, fmt):
        if fmt.key == 'json':
            return cls.load_json(collection, path, fmt)

        if fmt.key == 'mpack':
            return cls.load_mpack(collection, path, fmt)

        raise ValueError('Unknown index format: %s' % fmt)

    @classmethod
    def load_json(cls, collection, path, fmt):
        # Ensure directory for items exist
        items_path = os.path.join(os.path.dirname(path), 'items')

        if not os.path.exists(items_path):
            os.makedirs(items_path)

        # Construct new index (if one doesn't create yet)
        if not os.path.exists(path):
            return Index(collection, path, fmt)

        # Read json from file
        with open(path, 'rb') as fp:
            data = json.load(fp)

        # Construct index
        index = Index(collection, path, fmt)

        # Parse items
        index.items = dict([
            (key, Metadata.parse(value, index, key))
            for key, value in data.items()
        ])

        return index

    @classmethod
    def load_mpack(cls, collection, path, fmt):
        # Ensure directory for items exist
        items_path = os.path.join(os.path.dirname(path), 'items')

        if not os.path.exists(items_path):
            os.mkdir(items_path)

        # Construct new index (if one doesn't create yet)
        if not os.path.exists(path):
            return Index(collection, path, fmt)

        # Read json from file
        with open(path, 'rb') as fp:
            data = msgpack.unpack(fp)

        # Construct index
        index = Index(collection, path, fmt)

        # Parse items
        index.items = dict([
            (key, Metadata.parse(value, index, key))
            for key, value in data.items()
        ])

        return index

    def __repr__(self):
        source = self.collection.source
        target = self.collection.target

        if source and target:
            return '<Index %s -> %s (%s)>' % (
                source,
                target,
                self.format.extension if self.format else None
            )

        return '<Index %s (%s)>' % (
            source or target,
            self.format.extension if self.format else None
        )
