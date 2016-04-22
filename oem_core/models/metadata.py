from oem_core.core.minimize import Protocol
from oem_core.models import Item

import os


class Metadata(object):
    __slots__ = ['index', 'key', 'revision', 'hashes', 'media']

    def __init__(self, index, key, revision=0, hashes=None, media=None):
        self.index = index
        self.key = key

        self.revision = revision
        self.hashes = hashes or {}

        self.media = media

    def to_dict(self):
        result = {
            'revision': self.revision,
            'hashes': self.hashes,

            'media': self.media
        }

        # if minimal:
        #     return Minimize.encode(result, MetadataProtocol)

        return result

    def get(self):
        return Item.load(
            os.path.join(self.index.item_path, self.key),
            self.index.format,
            index=self.index
        )

    def update(self, item, hash_key, hash):
        item_path = os.path.join(self.index.item_path, self.key)

        if not item.write(item_path, self.index.format):
            # Unable to write item to disk
            return False

        # Update metadata
        if not self.hashes or hash_key in self.hashes:
            self.revision += 1

        self.hashes[hash_key] = hash

        self.media = item.media
        return True

    @classmethod
    def parse(cls, data, index=None, key=None):
        if data.get('~') == '~':
            # Parse "minimal" data structure
            return Metadata(
                index, key,
                MetadataProtocol.get_value(data, MetadataProtocol.revision),
                MetadataProtocol.get_value(data, MetadataProtocol.hashes),
                MetadataProtocol.get_value(data, MetadataProtocol.structure, 'single')
            )

        # Parse "full" data structure
        return Metadata(
            index, key,
            data.get('revision'),
            data.get('hashes'),
            data.get('media')
        )


class MetadataProtocol(Protocol):
    __root__ = True

    minimal     = 0x00

    revision    = 0x01
    hashes      = 0x02

    structure   = 0x03

    class HashesProtocol(Protocol):
        __key__ = 'hashes'
        __ignore__ = True
