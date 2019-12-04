""" SKALE chain test """

from skale.utils.constants import SCHAIN_TYPES
from tests.constants import LIFETIME_SECONDS


def test_get_schain_price(skale):
    for schain_type in SCHAIN_TYPES:
        schain_price = skale.schains.get_schain_price(SCHAIN_TYPES[schain_type],
                                                      LIFETIME_SECONDS)
        assert schain_price > 0
        assert type(schain_price) is int
