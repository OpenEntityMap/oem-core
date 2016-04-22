from tests.core.mock import MockCollection

from oem_core.models.episode import EpisodeMapping, Episode
from oem_core.models.show import Show
from oem_core.models.season import Season


def test_season_merge():
    collection = MockCollection('tvdb', 'anidb')

    current = Show(
        collection,

        identifiers={
            'anidb': 522,
            'tvdb': 103691
        },
        names={
            'Juusenki L-Gaim'
        },

        default_season='1'
    )

    #
    # Show 523
    #

    show_523 = Show(
        collection,

        identifiers={
            'anidb': 523,
            'tvdb': 103691
        },
        names={
            'Heavy Metal L-Gaim I: Pentagona Window + Lady Gavlet'
        },

        default_season='0'
    )

    #
    # Show 2488
    #

    show_2488 = Show(
        collection,

        identifiers={
            'anidb': 2488,
            'tvdb': 103691
        },
        names={
            'Heavy Metal L-Gaim II: Farewell My Lovely + Pentagona Dolls'
        },

        default_season='0'
    )

    show_2488.seasons['0'] = Season(collection, show_2488, '0')
    show_2488.seasons['0'].episodes = {'2': Episode(collection, show_2488.seasons['0'], '2'),}
    show_2488.seasons['0'].episodes['2'].mappings = [EpisodeMapping(collection, show_2488.seasons['0'].episodes['2'], '1', '1')]

    #
    # Show 2489
    #

    show_2489 = Show(
        collection,

        identifiers={
            'anidb': 2489,
            'tvdb': 103691
        },
        names={
            'Heavy Metal L-Gaim III: Fullmetal Soldier'
        },

        default_season='0'
    )

    show_2489.seasons['0'] = Season(collection, show_2489, '0')
    show_2489.seasons['0'].episodes = {'3': Episode(collection, show_2489.seasons['0'], '3'),}
    show_2489.seasons['0'].episodes['3'].mappings = [EpisodeMapping(collection, show_2489.seasons['0'].episodes['3'], '1', '1')]

    current.add(show_523, 'tvdb')
    current.add(show_2488, 'tvdb')
    current.add(show_2489, 'tvdb')

    # Validate merge result
    assert current.identifiers.get('tvdb') == 103691
    assert len(current.names) == 0

    # - Validate keys
    assert sorted(current.seasons.keys()) == ['0', '1']
    assert sorted(current.seasons['0'].episodes.keys()) == ['2', '3']
    assert sorted(current.seasons['1'].episodes.keys()) == []

    # - Validate season identifiers
    assert current.seasons['0'].identifiers.get('anidb') == 523
    assert current.seasons['1'].identifiers.get('anidb') == 522

    # - Validate episode identifiers
    assert current.seasons['0'].episodes['2'].identifiers.get('anidb') == 2488
    assert current.seasons['0'].episodes['3'].identifiers.get('anidb') == 2489
