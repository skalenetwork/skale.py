"""Tests for contracts/delegation/delegation_period_manager.py"""

import random

STAKE_MULTIPLIER = 100
CUSTOM_DELEGATION_PERIOD = 51


def test_set_delegation_period(skale):
    new_delegation_period = random.randint(13, 50)
    assert not skale.delegation_period_manager.is_delegation_period_allowed(new_delegation_period)
    skale.delegation_period_manager.set_delegation_period(
        months_count=new_delegation_period, stake_multiplier=STAKE_MULTIPLIER, wait_for=True
    )
    assert skale.delegation_period_manager.is_delegation_period_allowed(new_delegation_period)


def test_is_delegation_period_allowed(skale):
    assert not skale.delegation_period_manager.is_delegation_period_allowed(
        months_count=CUSTOM_DELEGATION_PERIOD
    )
