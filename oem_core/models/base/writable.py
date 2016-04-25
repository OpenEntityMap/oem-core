from oem_core.models.format import Format

import json
import logging
import msgpack
import os

log = logging.getLogger(__name__)

SUPPORTED_FORMATS = [
    'json',
    'mpack'
]


class Writable(object):
    __slots__ = ['path']

    def __init__(self, path=None):
        self.path = path

    def to_dict(self):
        raise NotImplementedError

    def write(self, path=None, fmt=None):
        if path is None:
            if self.path is not None:
                path = self.path

                if fmt and not path.endswith(fmt.extension):
                    raise ValueError('Extension mismatch, path is %r but format extension is %r' % (path, fmt.extension))
                elif not fmt:
                    fmt = Format.from_extension(os.path.splitext(path)[1].lstrip('.'))
            else:
                raise ValueError('Missing required "path" parameter')
        else:
            # Append `fmt` extension
            path = '%s.%s' % (path, fmt.extension)

        if fmt.minimal:
            raise NotImplementedError

        # Convert object to dictionary
        data = self.to_dict()

        try:
            # Write `data` to `path`
            self._write_data(data, path, fmt)
        except Exception, ex:
            # Unable to write item to disk
            log.error('Unable to write item to disk - %s', ex, exc_info=True)
            return False

        # Item successfully written to disk
        return True

    @staticmethod
    def _write_data(data, path, fmt):
        if fmt.key not in SUPPORTED_FORMATS:
            log.warn('Unsupported item format: %r', fmt)
            return False

        with open(path, 'wb') as fp:
            if fmt.key == 'json':
                json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))
                return True

            if fmt.key == 'mpack':
                msgpack.dump(data, fp)
                return True

        log.warn('Unknown item format: %r', fmt)
        return False

    @classmethod
    def load(cls, collection, path, fmt=None, **kwargs):
        if not path:
            raise ValueError('Invalid value provided for "path" parameter')

        if fmt:
            # Append `fmt` extension to `path`
            path = '%s.%s' % (path, fmt.extension)
        else:
            # Parse `fmt` from `path`
            fmt = Format.from_extension(os.path.splitext(path)[1].lstrip('.'))

        if not fmt:
            raise ValueError('Invalid value provided for "fmt" parameter')

        # Load data from disk
        data = None

        with open(path, 'rb') as fp:
            if fmt.key == 'json':
                data = json.load(fp)
            elif fmt.key == 'mpack':
                data = msgpack.load(fp)
            else:
                raise ValueError('Unsupported format: %r' % fmt)

        if not data:
            return None

        # Parse item
        return cls.parse(collection, data, **kwargs)

    @classmethod
    def parse(cls, collection, data, **kwargs):
        raise NotImplementedError
