from oem_framework.format import Format
from oem_framework.models.core import ModelRegistry
from oem_framework import models

import logging
import os

log = logging.getLogger(__name__)


class Collection(models.Collection):
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
        collection.index = ModelRegistry['Index'].load(collection, os.path.join(path, 'index.%s' % fmt.__extension__), fmt)

        # Construct collection
        return collection
