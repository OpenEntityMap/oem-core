from oem_core.core.helpers import get_attribute
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
        # Ensure item is different
        if self == item:
            return True

        # Demote current show to a season
        if self.collection.target in self.identifiers and not self.demote(service):
            return False

        # Add seasons to current show
        season_numbers = set([
            s.number for s in item.seasons.itervalues()
        ] + [
            item.parameters.get('default_season')
        ])

        error = False

        for season_num in season_numbers:
            # Construct season
            season = Season.from_show(self, season_num, item)

            if season_num in self.seasons:
                # Update existing season
                if not self.seasons[season_num].add(season, service):
                    error = True

                continue

            # Store new season
            self.seasons[season_num] = season

        return not error

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

    def demote(self, service):
        # Update existing seasons
        for season_num, season in self.seasons.items():
            self.seasons[season_num].update(
                identifiers=self.identifiers,
                names=self.names,

                supplemental=self.supplemental,
                parameters=self.parameters
            )

        # Retrieve season number
        season_num = self.parameters.get('default_season')

        if season_num is None:
            raise NotImplementedError

        # Create season from current show
        season = Season.from_show(self, season_num, self)

        if season_num in self.seasons:
            self.seasons[season_num].add(season, service)
        else:
            self.seasons[season_num] = Season.from_show(self, season_num, self)

        # Clear show
        return self.clear()

    @classmethod
    def parse(cls, collection, data, **kwargs):
        touched = set()

        # Construct movie
        show = cls(
            collection,

            identifiers=get_attribute(touched, data, 'identifiers'),
            names=set(get_attribute(touched, data, 'names', [])),

            supplemental=get_attribute(touched, data, 'supplemental', {}),
            **get_attribute(touched, data, 'parameters', {})
        )

        # Construct seasons
        if 'seasons' in data:
            show.seasons = dict([
                (k, Season.parse(collection, v, key=k, parent=show))
                for k, v in get_attribute(touched, data, 'seasons').items()
            ])

        # Ensure all attributes were touched
        omitted = set(data.keys()) - touched

        if omitted:
            log.warn('Show.parse() omitted %d attribute(s): %s', len(omitted), ', '.join(omitted))

        return show

    def to_dict(self, key=None):
        if self.identifiers.get('tvdb') == '76703' and '16' in self.seasons:
            pass

        result = super(Show, self).to_dict(key=key)

        if self.identifiers.get('tvdb') == '76703' and '16' in self.seasons:
            pass

        return result

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        if self.identifiers and self.names:
            service = self.identifiers.keys()[0]

            return '<Show %s: %r, names: %r>' % (
                service,
                self.identifiers[service],
                self.names
            )

        if self.identifiers:
            service = self.identifiers.keys()[0]

            return '<Show %s: %r>' % (
                service,
                self.identifiers[service]
            )

        if self.names:
            return '<Show names: %r>' % (
                self.names
            )

        return '<Show>'
