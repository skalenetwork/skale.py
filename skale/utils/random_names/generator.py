#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import random
from skale.utils.random_names.vocabulary import (
    CONSTELLATIONS,
    STARS,
    SOUND_AND_APPEARANCE_ADJECTIVES,
    POSITIVE_AND_TIME_ADJECTIVES,
)


def generate_random_node_name() -> str:
    return generate_name(CONSTELLATIONS, POSITIVE_AND_TIME_ADJECTIVES)


def generate_random_schain_name() -> str:
    return generate_name(STARS, SOUND_AND_APPEARANCE_ADJECTIVES)


def generate_name(noun_dict: list[str], adjective_dict: list[str]) -> str:
    noun = get_random_word_from_dict(noun_dict)
    adjective = get_random_word_from_dict(adjective_dict)
    return f'{adjective}-{noun}'


def get_random_word_from_dict(vocabulary_dict: list[str]) -> str:
    return random.choice(vocabulary_dict).lower().replace(' ', '-')


if __name__ == '__main__':
    node_name = generate_random_node_name()
    schain_name = generate_random_schain_name()
    print(f'Node name: {node_name}, sChain name: {schain_name}')
