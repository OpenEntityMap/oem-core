from oem_framework import models
from oem_framework.models.core import ModelRegistry

import os


class Metadata(models.Metadata):
    def get(self):
        return self.index.format.from_path(
            self.collection,
            model=ModelRegistry['Item'],
            path=os.path.join(self.index.items_path, self.key),

            # Parameters
            media=self.media
        )
