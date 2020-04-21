from tests.constants import MONTH_IN_SECONDS


def test_get_current_month(skale):
    current_month = skale.time_helpers_with_debug.get_current_month()
    assert isinstance(current_month, int)
    assert current_month <= 12


def test_skip_time(skale):
    current_month_before = skale.time_helpers_with_debug.get_current_month()
    skale.time_helpers_with_debug.skip_time(MONTH_IN_SECONDS, wait_for=True)
    current_month_after = skale.time_helpers_with_debug.get_current_month()
    assert current_month_after == current_month_before + 1
