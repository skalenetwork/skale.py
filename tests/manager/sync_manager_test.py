import pytest
from web3.exceptions import ContractLogicError

from skale.transactions.exceptions import DryRunRevertError

START_IP = '0.0.0.1'
END_IP = '255.255.255.254'


@pytest.fixture
def sync_manager_permissions(skale):
    skale.sync_manager.grant_sync_manager_role(skale.wallet.address)


@pytest.fixture
def ip_range(skale):
    name = 'test-range'
    skale.sync_manager.add_ip_range(name, START_IP, END_IP)
    try:
        yield name
    finally:
        skale.sync_manager.remove_ip_range(name)


def test_add_get_remove_ip_range(skale, sync_manager_permissions, ip_range, block_in_seconds):
    r = skale.sync_manager.get_ip_range_by_name(ip_range)
    assert r.start_ip == START_IP
    assert r.end_ip == END_IP

    r = skale.sync_manager.get_ip_range_by_index(0)
    assert r.start_ip == START_IP
    assert r.end_ip == END_IP


def test_add_bad_ip_range(skale, sync_manager_permissions, block_in_seconds):
    with pytest.raises(DryRunRevertError):
        skale.sync_manager.add_ip_range('brange', '0.0.0.0', '1.1.1.1')

    with pytest.raises(DryRunRevertError):
        skale.sync_manager.add_ip_range('brange', '2.2.2.2', '1.1.1.1')

    with pytest.raises(OSError):
        skale.sync_manager.add_ip_range('brange', '1.1.1.1', '256.256.256.256')


def test_remove_range_bad_params(skale, sync_manager_permissions, block_in_seconds):
    with pytest.raises(DryRunRevertError):
        skale.sync_manager.remove_ip_range('phantom')


def test_get_range_bad_params(skale, sync_manager_permissions, block_in_seconds):
    num = skale.sync_manager.get_ip_ranges_number()
    # TODO: Make dry run handle revert that has empty reason properly
    with pytest.raises(ContractLogicError):
        r = skale.sync_manager.get_ip_range_by_index(num)
    with pytest.raises(ContractLogicError):
        r = skale.sync_manager.get_ip_range_by_index(0)
    r = skale.sync_manager.get_ip_range_by_name('phantom')
    assert r.start_ip == '0.0.0.0' and r.end_ip == '0.0.0.0'
