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
        # Ensure item is different
        if self == item:
            return True

        # Break season into episodes (if we are merging episodes
        if (self.episodes or item.episodes) and self.collection.target in self.identifiers and not self.demote():
            return False

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
                    if type(self.episodes[key]) is list:
                        # Ensure `episode` isn't already in season
                        for ep in self.episodes[key]:
                            if ep == episode:
                                return True
                    elif self.episodes[key] == episode:
                        return True

                    # Convert to episodes list
                    if type(self.episodes[key]) is not list:
                        current = self.episodes[key]
                        # TODO update `current` with `names` and `identifiers`

                        self.episodes[key] = [current]

                    # Add additional episode
                    self.episodes[key].append(episode)
                    continue

                self.episodes[key] = episode

            return True

        if episode_num is None:
            # Copy attributes
            for service, key in item.identifiers.items():
                # Convert "identifiers" list to set type
                if service in self.identifiers and type(self.identifiers[service]) is list:
                    self.identifiers[service] = set(self.identifiers[service])

                # Update "identifiers"
                if service not in self.identifiers:
                    self.identifiers[service] = key
                elif type(self.identifiers[service]) is set:
                    self.identifiers[service].add(key)
                elif self.identifiers[service] != key:
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
            if type(self.episodes[episode_num]) is list:
                for ep in self.episodes[episode_num]:
                    if ep == episode:
                        return True
            elif self.episodes[episode_num] == episode:
                return True

            log.warn('Conflict detected, episode %r already exists', episode_num)
            return False

        self.episodes[episode_num] = episode

        # Add season mappings
        for mapping in item.mappings:
            # Check for duplicate mapping
            matched = any([mapping == m for m in self.mappings])

            if matched:
                continue

            # Update mapping
            mapping.identifiers = deepcopy(item.identifiers)

            for name in item.names:
                mapping.names.add(name)

            # Store mapping in current season
            self.mappings.append(mapping)

        return True

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

    def demote(self):
        demoted = False

        # Demote season (with episode offset)
        episode_offset = self.parameters.get('episode_offset')

        if episode_offset is not None:
            try:
                episode_num = str(int(episode_offset) + 1)
            except ValueError, ex:
                log.warn('Unable parse episode offset %r - %s', episode_offset, ex, exc_info=True)
                episode_num = episode_offset

            # Create episode from current season
            episode = Episode.from_season(episode_num, self)

            if episode_num not in self.episodes:
                self.episodes[episode_num] = episode
            else:
                log.warn('Conflict detected, episode %r already exists', episode_num)

            demoted = True

        # Demote episodes
        if self.episodes:
            target_identifier = self.identifiers.get(self.collection.target)

            for key, episodes in self.episodes.items():
                if type(episodes) is not list:
                    episodes = [episodes]

                for episode in episodes:
                    if episode.identifiers:
                        # Check for episode identifier match
                        if target_identifier == episode.identifiers.get(self.collection.target):
                            demoted = True

                        continue

                    # Update episode
                    episode.identifiers = deepcopy(self.identifiers)

                    for name in self.names:
                        episode.names.add(name)

                    episode.supplemental = episode.supplemental or deepcopy(self.supplemental)
                    episode.parameters = episode.parameters or deepcopy(self.parameters)

                    demoted = True

        # Demote mappings
        if self.mappings:
            target_identifier = self.identifiers.get(self.collection.target)

            for mapping in self.mappings:
                if mapping.identifiers:
                    # Check for episode identifier match
                    if target_identifier == mapping.identifiers.get(self.collection.target):
                        demoted = True

                    continue

                # Update mapping
                mapping.identifiers = deepcopy(self.identifiers)

                for name in self.names:
                    mapping.names.add(name)

                demoted = True

        if demoted:
            # Clear season attributes
            return self.clear()

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

        default_season = parameters.pop('default_season', None)

        if default_season != number and 'episode_offset' in parameters:
            del parameters['episode_offset']

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
            def parse_episodes():
                for k, v in get_attribute(touched, data, 'episodes').items():
                    if type(v) is list:
                        yield k, [
                            Episode.parse(collection, v_episode, key=k, parent=season)
                            for v_episode in v
                        ]
                    else:
                        yield k, Episode.parse(collection, v, key=k, parent=season)

            season.episodes = dict(parse_episodes())

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

    def update(self, identifiers=None, names=None, supplemental=None, parameters=None):
        # Copy attributes
        for service, key in (identifiers or {}).items():
            # Ignore source keys
            if self.collection.source == service:
                continue

            # Convert "identifiers" list to set type
            if service in self.identifiers and type(self.identifiers[service]) is list:
                self.identifiers[service] = set(self.identifiers[service])

            # Update "identifiers"
            if service not in self.identifiers:
                self.identifiers[service] = key
            elif type(self.identifiers[service]) is set:
                self.identifiers[service].add(key)
            elif self.identifiers[service] != key:
                self.identifiers[service] = {self.identifiers[service], key}

        for name in (names or []):
            self.names.add(name)

        if supplemental is not None:
            self.supplemental.update(supplemental)

        if parameters is not None:
            self.parameters.update(parameters)

            if 'default_season' in self.parameters:
                del self.parameters['default_season']

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
    __slots__ = ['identifiers', 'names', 'season', 'start', 'end', 'offset']

    def __init__(self, collection, season, start, end, offset, identifiers=None, names=None):
        super(SeasonMapping, self).__init__(collection)

        self.identifiers = identifiers or {}
        self.names = names or set()

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

            identifiers=get_attribute(touched, data, 'identifiers'),
            names=set(get_attribute(touched, data, 'names', [])),

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
        result = {
            'season': self.season,

            'start': self.start,
            'end': self.end,

            'offset': self.offset
        }

        if self.identifiers:
            result['identifiers'] = self.identifiers

        if self.names:
            result['names'] = list(self.names)

        return result

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()
