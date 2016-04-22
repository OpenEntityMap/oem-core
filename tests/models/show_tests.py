from tests.core.mock import MockCollection

from oem_core.models.episode import Episode, EpisodeMapping
from oem_core.models.show import Show
from oem_core.models.season import Season


def test_merge_season_with_episodes():
    collection = MockCollection('tvdb', 'anidb')

    current = Show(
        collection,
        identifiers={
            'anidb': 4057,
            'tvdb': 71419
        },
        names={
            'Kinnikuman II Sei: Ultimate Muscle 2'
        },

        default_season='3'
    )

    show_2134 = Show(
        collection,
        identifiers={
            'anidb': 2134,
            'tvdb': 71419
        },
        names={
            'Kinnikuman II Sei: Ultimate Muscle'
        },

        default_season='3'
    )

    show_2134.seasons['3'] = Season(collection, show_2134, '3')

    show_2134.seasons['3'].episodes = {
        '14': Episode(collection, show_2134.seasons['3'], '14'),
        '15': Episode(collection, show_2134.seasons['3'], '15'),
        '16': Episode(collection, show_2134.seasons['3'], '16')
    }

    show_2134.seasons['3'].episodes['14'].mappings = [EpisodeMapping(collection, show_2134.seasons['3'].episodes['14'], '1', '1')]
    show_2134.seasons['3'].episodes['15'].mappings = [EpisodeMapping(collection, show_2134.seasons['3'].episodes['15'], '1', '2')]
    show_2134.seasons['3'].episodes['16'].mappings = [EpisodeMapping(collection, show_2134.seasons['3'].episodes['16'], '1', '3')]

    current.add(show_2134, 'tvdb')

    assert len(current.names) == 0
    assert len(current.seasons) == 1

    assert '3' in current.seasons
    assert len(current.seasons['3'].episodes) == 3

    assert current.seasons['3'].identifiers == {'anidb': 4057}
    assert current.seasons['3'].names == {'Kinnikuman II Sei: Ultimate Muscle 2'}

    assert current.seasons['3'].episodes['14'].identifiers == {'anidb': 2134}
    assert current.seasons['3'].episodes['14'].names == {'Kinnikuman II Sei: Ultimate Muscle'}


def test_merge_episodes_with_season():
    collection = MockCollection('tvdb', 'anidb')

    current = Show(
        collection,
        identifiers={
            'anidb': 2134,
            'tvdb': 71419
        },
        names={
            'Kinnikuman II Sei: Ultimate Muscle'
        },

        default_season='3'
    )

    current.seasons['3'] = Season(collection, current, '3')

    current.seasons['3'].episodes = {
        '14': Episode(collection, current.seasons['3'], '14'),
        '15': Episode(collection, current.seasons['3'], '15'),
        '16': Episode(collection, current.seasons['3'], '16')
    }

    current.seasons['3'].episodes['14'].mappings = [EpisodeMapping(collection, current.seasons['3'].episodes['14'], '1', '1')]
    current.seasons['3'].episodes['15'].mappings = [EpisodeMapping(collection, current.seasons['3'].episodes['15'], '1', '2')]
    current.seasons['3'].episodes['16'].mappings = [EpisodeMapping(collection, current.seasons['3'].episodes['16'], '1', '3')]

    current.add(Show(
        collection,
        identifiers={
            'anidb': 4057,
            'tvdb': 71419
        },
        names={
            'Kinnikuman II Sei: Ultimate Muscle 2'
        },

        default_season='3'
    ), 'tvdb')

    assert len(current.names) == 0
    assert len(current.seasons) == 1

    assert '3' in current.seasons
    assert len(current.seasons['3'].episodes) == 3

    assert current.seasons['3'].identifiers == {'anidb': 4057}
    assert current.seasons['3'].names == {'Kinnikuman II Sei: Ultimate Muscle 2'}

    assert current.seasons['3'].episodes['14'].identifiers == {'anidb': 2134}
    assert current.seasons['3'].episodes['14'].names == {'Kinnikuman II Sei: Ultimate Muscle'}
