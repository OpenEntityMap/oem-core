from oem_core.models.base import BaseMapping, BaseMedia

from copy import deepcopy


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
    __slots__ = ['parent', 'season', 'number']

    def __init__(self, collection, parent, season, number):
        super(EpisodeMapping, self).__init__(collection)
        self.parent = parent

        self.season = season
        self.number = number

    def to_dict(self, key=None):
        result = {}

        if self.season != self.parent.season:
            result['season'] = self.season

        if len(result) < 1 or self.number != self.parent.number:
            result['number'] = self.number

        return result
