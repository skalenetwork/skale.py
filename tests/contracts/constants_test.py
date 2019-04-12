import skale.utils.helper as Helper

from tests.constants import NEW_REWARD_PERIOD, NEW_DELTA_PERIOD


def test_set_periods(skale, wallet):
    res = skale.constants.set_periods(NEW_REWARD_PERIOD, NEW_DELTA_PERIOD, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])

    assert receipt['status'] == 1
