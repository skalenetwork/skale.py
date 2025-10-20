import pytest

from tests.constants import MONTH_IN_SECONDS


def test_get_current_month(skale):
    current_month = skale.time_helpers_with_debug.get_current_month()
    assert isinstance(current_month, int)
    assert 0 < current_month < 1200


@pytest.mark.skip('Not working. Fix later')
def test_skip_time(skale):
    current_month_before = skale.time_helpers_with_debug.get_current_month()
    skale.time_helpers_with_debug.skip_time(MONTH_IN_SECONDS + 1, wait_for=True)
    current_month_after = skale.time_helpers_with_debug.get_current_month()
    assert current_month_after == current_month_before + 1, (
        current_month_after,
        current_month_before,
    )
