import os
import random

from skale.utils.helper import read_file

CURRENT_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))

CONSTELLATIONS_FILENAME = 'constellations.txt'
CONSTELLATIONS_FILE = os.path.join(CURRENT_FILE_LOCATION, CONSTELLATIONS_FILENAME)

POS_AND_TIME_ADJECTIVES_FILENAME = 'positive-and-time-adjectives.txt'
POS_AND_TIME_ADJECTIVES_FILE = os.path.join(CURRENT_FILE_LOCATION, POS_AND_TIME_ADJECTIVES_FILENAME)

STARS_FILENAME = 'stars.txt'
STARS_FILE = os.path.join(CURRENT_FILE_LOCATION, STARS_FILENAME)

SOUND_AND_APPEARANCE_ADJECTIVES_FILENAME = 'sound-and-appearance-adjectives.txt'
SOUND_AND_APPEARANCE_ADJECTIVES_FILE = os.path.join(CURRENT_FILE_LOCATION,
                                                    SOUND_AND_APPEARANCE_ADJECTIVES_FILENAME)


def generate_random_node_name():
    return generate_name(CONSTELLATIONS_FILENAME, POS_AND_TIME_ADJECTIVES_FILE)


def generate_random_schain_name():
    return generate_name(STARS_FILE, SOUND_AND_APPEARANCE_ADJECTIVES_FILE)


def generate_name(noun_file, adjective_file):
    noun = get_random_word_from_file(noun_file)
    adjective = get_random_word_from_file(adjective_file)
    return f'{adjective}-{noun}'


def get_random_word_from_file(filename):
    txt = read_file(filename)
    words_list = txt.splitlines()
    return random.choice(words_list).lower().replace(" ", "-")


if __name__ == "__main__":
    node_name = generate_random_node_name()
    schain_name = generate_random_schain_name()
    print(f'Node name: {node_name}, sChain name: {schain_name}')
