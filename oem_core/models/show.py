from oem_core.models.base import BaseMedia
from oem_core.models.season import Season

import logging

log = logging.getLogger(__name__)


class Show(BaseMedia):
    __slots__ = ['names', 'mappings', 'seasons']
    __attributes__ = ['names', 'mappings', 'seasons']

    def __init__(self, collection, identifiers, names, mappings=None, seasons=None, **kwargs):
        super(Show, self).__init__(collection, 'show', identifiers, **kwargs)

        self.names = names or set()

        self.mappings = mappings or []
        self.seasons = seasons or {}

    def add(self, item, service):
        # Demote current show to a season
        if self.collection.target in self.identifiers and not self.demote():
            return False

        # Retrieve season number
        season_num = item.parameters.get('default_season')

        if season_num is None:
            if len(item.seasons) < 1:
                raise NotImplementedError

            season_num = item.seasons.values()[0].number

        # Add additional season
        season = Season.from_show(self, season_num, item)

        if season_num in self.seasons:
            if not self.seasons[season_num].add(season, service):
                log.warn('Unable add season %r to %r (show: %r)', season, self.seasons[season_num], self)
                return False

            return True

        self.seasons[season_num] = season
        return True

    def demote(self):
        # Retrieve season number
        season_num = self.parameters.get('default_season')

        if season_num is None:
            raise NotImplementedError

        # Create season from current show
        self.seasons = {season_num: Season.from_show(self, season_num, self)}

        # Clear show
        return self.clear()

    def clear(self):
        if self.collection.target not in self.identifiers:
            return False

        # Reset attributes
        self.names = set()

        self.supplemental = {}
        self.parameters = {}

        # Remove target collection identifier
        del self.identifiers[self.collection.target]
        return True

    def __repr__(self):
        if self.identifiers:
            service = self.identifiers.keys()[0]

            return '<Show %s: %r, names: %r>' % (
                service,
                self.identifiers[service],
                self.names
            )

        return '<Show names: %r>' % (
            self.names,
        )
