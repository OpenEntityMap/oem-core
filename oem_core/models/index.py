from oem_framework import models

import logging
import os

log = logging.getLogger(__name__)


class Index(models.Index):
    @classmethod
    def load(cls, collection, path, fmt):
        # Ensure directory for items exist
        items_path = os.path.join(os.path.dirname(path), 'items')

        if not os.path.exists(items_path):
            os.makedirs(items_path)

        # Construct new index (if one doesn't create yet)
        if not os.path.exists(path):
            return cls(collection, path, fmt)

        # Load index from path
        return fmt.from_path(
            collection, cls, path,
            fmt=fmt
        )
