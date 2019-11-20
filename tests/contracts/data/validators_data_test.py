""" SKALE validators data test """

from tests.constants import DEFAULT_NODE_ID


def test_get_reward_period(skale):
    reward_period = skale.validators_data.get_reward_period()
    assert type(reward_period) is int


def test_get_delta_period(skale):
    delta_period = skale.validators_data.get_delta_period()
    assert type(delta_period) is int


def test_get_validated_array(skale):
    validated_array = skale.validators_data.get_validated_array(DEFAULT_NODE_ID)
    assert type(validated_array) is list
