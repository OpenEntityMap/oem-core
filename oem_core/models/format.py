import os


FORMAT_SETTINGS = {
    "json": {
        "hash_format": "hex"
    },
    "mpack": {
        "hash_format": "unicode"
    }
}


class Format(object):
    def __init__(self, extension, key, hash_format="hex", minimal=False):
        self.extension = extension
        self.key = key

        self.hash_format = hash_format
        self.minimal = minimal

    @classmethod
    def from_extension(cls, extension):
        # Retrieve format key
        dot_pos = extension.rfind(".")

        if dot_pos >= 0:
            key = extension[dot_pos + 1:]
        else:
            key = extension

        # Construct `Format` object
        return cls(
            extension, key,
            minimal=extension.startswith('min.'),
            **FORMAT_SETTINGS[key]
        )

    @classmethod
    def from_path(cls, path):
        filename = os.path.basename(path)

        # Find extension in filename
        dot_start = filename.find('.')

        if dot_start < 0:
            raise ValueError('Unable to find extension in filename: %r' % filename)

        extension = filename[dot_start + 1:]

        # Construct format from `extension`
        return cls.from_extension(extension)

    def __repr__(self):
        return '<Format extension: %r, hash_format: %r, minimal: %r>' % (
            self.extension,
            self.hash_format,
            self.minimal
        )
