from oem_core.core.helpers import get_attribute
from oem_core.models.base import BaseMapping, BaseMedia
from oem_core.models.range import Range

from copy import deepcopy
import logging

log = logging.getLogger(__name__)


class Episode(BaseMedia):
    __slots__ = ['parent', 'season', 'number', 'names', 'mappings']
    __attributes__ = ['season', 'number', 'names', 'mappings']

    def __init__(self, collection, parent, number, identifiers=None, names=None, mappings=None, **parameters):
        super(Episode, self).__init__(collection, 'episode', identifiers, **parameters)
        self.parent = parent

        self.season = parent.number
        self.number = number

        self.names = names or set()

        self.mappings = mappings or []

    @classmethod
    def from_season(cls, number, season):
        if not season:
            raise ValueError('Invalid value provided for "season"')

        # Build season identifiers
        identifiers = deepcopy(season.identifiers)

        if season.collection.source in identifiers:
            del identifiers[season.collection.source]

        # Build season parameters
        parameters = deepcopy(season.parameters)

        if 'default_season' in parameters:
            del parameters['default_season']

        # Construct season
        episode = Episode(
            season.collection,
            season,

            number,

            identifiers,
            season.names,

            supplemental=season.supplemental,
            **parameters
        )

        # Add extra details
        if season.episodes and number in season.episodes:
            episode.mappings = season.episodes[number].mappings

        return episode

    def to_dict(self, key=None):
        result = super(Episode, self).to_dict(key=key)

        # Remove "season" attribute if it matches the parent season
        if result.get('season') == self.parent.number:
            del result['season']

        # Remove "number" attribute if it matches the parent dictionary key
        if len(result) > 0 and key is not None and result.get('number') == key:
            del result['number']

        return result

    @classmethod
    def parse(cls, collection, data, key=None, parent=None, **kwargs):
        if key is None:
            raise ValueError('Missing required parameter: "key"')

        if parent is None:
            raise ValueError('Missing required parameter: "parent"')

        touched = set()

        # Construct movie
        episode = cls(
            collection,
            parent,
            key,

            identifiers=get_attribute(touched, data, 'identifiers'),
            names=set(get_attribute(touched, data, 'names', [])),

            supplemental=get_attribute(touched, data, 'supplemental', {}),
            **get_attribute(touched, data, 'parameters', {})
        )

        # Construct mappings
        if 'mappings' in data:
            episode.mappings = [
                EpisodeMapping.parse(collection, v, parent=episode)
                for v in get_attribute(touched, data, 'mappings')
            ]

        # Ensure all attributes were touched
        omitted = set(data.keys()) - touched

        if omitted:
            log.warn('Episode.parse() omitted %d attribute(s): %s', len(omitted), ', '.join(omitted))

        return episode

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        if self.identifiers and self.names:
            service = self.identifiers.keys()[0]

            return '<Episode %s: %r, names: %r>' % (
                service,
                self.identifiers[service],
                self.names
            )

        if self.identifiers:
            service = self.identifiers.keys()[0]

            return '<Episode %s: %r>' % (
                service,
                self.identifiers[service]
            )

        if self.names:
            return '<Episode names: %r>' % (
                self.names
            )

        return '<Episode>'


class EpisodeMapping(BaseMapping):
    __slots__ = ['parent', 'season', 'number', 'timeline']

    def __init__(self, collection, parent, season, number, timeline=None):
        super(EpisodeMapping, self).__init__(collection)
        self.parent = parent

        self.season = season
        self.number = number

        self.timeline = timeline or {}

    @classmethod
    def parse(cls, collection, data, parent=None, **kwargs):
        if parent is None:
            raise ValueError('Missing required parameter: "parent"')

        touched = set()

        # Construct episode mapping
        episode_mapping = cls(
            collection,
            parent,

            # Identifier
            season=get_attribute(touched, data, 'season', parent.season),
            number=get_attribute(touched, data, 'number', parent.number)
        )

        # Parse "timeline" attribute
        if 'timeline' in data:
            episode_mapping.timeline = dict([
                (k, Range.parse(collection, v))
                for k, v in get_attribute(touched, data, 'timeline', {}).items()
            ])

        # Ensure all attributes were touched
        omitted = set(data.keys()) - touched

        if omitted:
            log.warn('EpisodeMapping.parse() omitted %d attribute(s): %s', len(omitted), ', '.join(omitted))

        return episode_mapping

    def to_dict(self, key=None):
        result = {}

        # Identifier
        if self.season != self.parent.season:
            result['season'] = self.season

        if len(result) < 1 or self.number != self.parent.number:
            result['number'] = self.number

        # Range
        if self.timeline:
            def iterator():
                for k, v in self.timeline.items():
                    v = v.to_dict()

                    if not v:
                        continue

                    yield k, v

            timeline = dict(iterator())

            if timeline:
                result['timeline'] = timeline

        return result

    def __eq__(self, other):
        return self.to_dict() != other.to_dict()
