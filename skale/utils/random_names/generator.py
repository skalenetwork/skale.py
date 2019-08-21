import random
from skale.utils.random_names.vocabulary import CONSTELLATIONS, STARS, \
    SOUND_AND_APPEARANCE_ADJECTIVES, POSITIVE_AND_TIME_ADJECTIVES


def generate_random_node_name():
    return generate_name(CONSTELLATIONS, POSITIVE_AND_TIME_ADJECTIVES)


def generate_random_schain_name():
    return generate_name(STARS, SOUND_AND_APPEARANCE_ADJECTIVES)


def generate_name(noun_dict, adjective_dict):
    noun = get_random_word_from_dict(noun_dict)
    adjective = get_random_word_from_dict(adjective_dict)
    return f'{adjective}-{noun}'


def get_random_word_from_dict(vocabulary_dict):
    return random.choice(vocabulary_dict).lower().replace(" ", "-")


if __name__ == "__main__":
    node_name = generate_random_node_name()
    schain_name = generate_random_schain_name()
    print(f'Node name: {node_name}, sChain name: {schain_name}')
