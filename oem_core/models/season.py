from oem_core.core.helpers import get_attribute
from oem_core.models.episode import Episode
from oem_core.models.base import BaseMapping, BaseMedia

from copy import deepcopy
import logging

log = logging.getLogger(__name__)


class Season(BaseMedia):
    __slots__ = ['parent', 'number', 'names', 'mappings', 'episodes']
    __attributes__ = ['number', 'names', 'mappings', 'episodes']

    def __init__(self, collection, parent, number, identifiers=None, names=None, mappings=None, episodes=None, **parameters):
        super(Season, self).__init__(collection, 'season', identifiers, **parameters)
        self.parent = parent

        self.number = number

        self.names = names or set()

        self.mappings = mappings or []
        self.episodes = episodes or {}

    def add(self, item, service):
        if self.identifiers:
            # Demote current season
            self.demote()

        # Retrieve episode number
        episode_num = None

        if len(item.episodes) == 0:
            if item.parameters.get('episode_offset'):
                try:
                    episode_num = str(int(item.parameters['episode_offset']) + 1)
                except ValueError:
                    episode_num = item.parameters['episode_offset']
        elif len(item.episodes) == 1:
            # Use number of first episode in season
            episode_num = item.episodes.keys()[0]
        else:
            # Add additional episodes from season
            for key, episode in item.episodes.items():
                episode.identifiers = episode.identifiers or deepcopy(item.identifiers)

                for name in item.names:
                    episode.names.add(name)

                episode.supplemental = episode.supplemental or deepcopy(item.supplemental)
                episode.parameters = episode.parameters or deepcopy(item.parameters)

                if key in self.episodes:
                    if type(self.episodes[key]) is not list:
                        current = self.episodes[key]
                        # TODO update `current` with `names` and `identifiers`

                        self.episodes[key] = [current]

                    self.episodes[key].append(episode)
                    continue

                self.episodes[key] = episode

            return True

        if episode_num is None:
            # Copy attributes
            for service, key in item.identifiers.items():
                if service not in self.identifiers:
                    self.identifiers[service] = key
                elif type(self.identifiers[service]) is set:
                    self.identifiers[service].add(key)
                else:
                    self.identifiers[service] = {self.identifiers[service], key}

            for name in item.names:
                self.names.add(name)

            self.supplemental.update(item.supplemental)
            self.parameters.update(item.parameters)

            for key, episode in item.episodes.items():
                if key in self.episodes:
                    raise NotImplementedError

                self.episodes[key] = episode

            return True

        if episode_num == '0':
            return True

        # Add additional episode
        episode = Episode.from_season(episode_num, item)

        if episode_num in self.episodes:
            log.warn('Conflict detected, episode %r already exists', episode_num)
            return False

        self.episodes[episode_num] = episode
        return True

    def demote(self):
        episode_offset = self.parameters.get('episode_offset')

        if episode_offset is not None:
            try:
                episode_num = str(int(episode_offset) + 1)
            except ValueError, ex:
                log.warn('Unable parse episode offset %r - %s', episode_offset, ex, exc_info=True)
                episode_num = episode_offset

            # Create episode from current season
            self.episodes = {episode_num: Episode.from_season(episode_num, self)}
        elif self.episodes:
            copied_keys = []

            for key, episode in self.episodes.items():
                if episode.identifiers:
                    continue

                episode.identifiers = deepcopy(self.identifiers)

                for name in self.names:
                    episode.names.add(name)

                episode.supplemental = episode.supplemental or deepcopy(self.supplemental)
                episode.parameters = episode.parameters or deepcopy(self.parameters)

                copied_keys.append(key)

            if len(copied_keys) <= 0:
                # No episodes were copied
                return True
        else:
            return True

        # Remove old attributes
        self.identifiers = {}
        self.names = set()

        self.supplemental = {}
        self.parameters = {}

        # Update show identifiers
        if self.collection.target in self.identifiers:
            self.identifiers.pop(self.collection.target)

        return True

    @classmethod
    def from_show(cls, show, number, item):
        if not item:
            raise ValueError('Invalid value provided for "show"')

        # Build season identifiers
        identifiers = deepcopy(item.identifiers)
        identifiers.pop(item.collection.source)

        # Build season parameters
        parameters = deepcopy(item.parameters)
        del parameters['default_season']

        # Construct season
        season = Season(
            item.collection,

            show,
            number,

            identifiers,
            item.names,

            supplemental=item.supplemental,
            **parameters
        )

        # Add extra details
        if item.seasons and number in item.seasons:
            season.episodes = item.seasons[number].episodes
            season.mappings = item.seasons[number].mappings

        if season.parameters is None:
            pass

        return season

    @classmethod
    def parse(cls, collection, data, key=None, parent=None, **kwargs):
        if key is None:
            raise ValueError('Missing required parameter: "key"')

        if parent is None:
            raise ValueError('Missing required parameter: "parent"')

        touched = set()

        # Construct movie
        season = cls(
            collection,
            parent,
            key,

            identifiers=get_attribute(touched, data, 'identifiers'),
            names=set(get_attribute(touched, data, 'names', [])),

            supplemental=get_attribute(touched, data, 'supplemental', {}),
            **get_attribute(touched, data, 'parameters', {})
        )

        # Construct episodes
        if 'episodes' in data:
            season.episodes = dict([
                (k, Episode.parse(collection, v, key=k, parent=season))
                for k, v in get_attribute(touched, data, 'episodes').items()
            ])

        # Construct mappings
        if 'mappings' in data:
            season.mappings = [
                SeasonMapping.parse(collection, v, parent=season)
                for v in get_attribute(touched, data, 'mappings')
            ]

        # Ensure all attributes were touched
        omitted = set(data.keys()) - touched

        if omitted:
            log.warn('Season.parse() omitted %d attribute(s): %s', len(omitted), ', '.join(omitted))

        return season

    def to_dict(self, key=None):
        result = super(Season, self).to_dict(key=key)

        # Remove "number" attribute if it matches the parent dictionary key
        if len(result) > 0 and key is not None and result.get('number') == key:
            del result['number']

        return result

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        if self.identifiers and self.names:
            service = self.identifiers.keys()[0]

            return '<Season %s: %r, names: %r>' % (
                service,
                self.identifiers[service],
                self.names
            )

        if self.identifiers:
            service = self.identifiers.keys()[0]

            return '<Season %s: %r>' % (
                service,
                self.identifiers[service]
            )

        if self.names:
            return '<Season names: %r>' % (
                self.names,
            )

        return '<Season>'


class SeasonMapping(BaseMapping):
    __slots__ = ['season', 'start', 'end', 'offset']

    def __init__(self, collection, season, start, end, offset):
        super(SeasonMapping, self).__init__(collection)

        self.season = season

        self.start = start
        self.end = end

        self.offset = offset

    @classmethod
    def parse(cls, collection, data, **kwargs):
        touched = set()

        # Construct episode mapping
        season_mapping = cls(
            collection,

            season=get_attribute(touched, data, 'season'),

            start=get_attribute(touched, data, 'start'),
            end=get_attribute(touched, data, 'end'),

            offset=get_attribute(touched, data, 'offset')
        )

        # Ensure all attributes were touched
        omitted = set(data.keys()) - touched

        if omitted:
            log.warn('SeasonMapping.parse() omitted %d attribute(s): %s', len(omitted), ', '.join(omitted))

        return season_mapping

    def to_dict(self, key=None):
        return {
            'season': self.season,

            'start': self.start,
            'end': self.end,

            'offset': self.offset
        }
