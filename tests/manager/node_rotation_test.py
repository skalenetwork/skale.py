""" SKALE node rotation test """

import mock

from skale.contracts.manager.node_rotation import Rotation
from tests.constants import DEFAULT_SCHAIN_ID, DEFAULT_SCHAIN_NAME, DEFAULT_SCHAIN_INDEX


def test_get_rotation(skale):
    assert skale.node_rotation.get_rotation(DEFAULT_SCHAIN_NAME) == {
        'leaving_node': 0,
        'new_node': 0,
        'finish_ts': 0,
        'rotation_id': 0
    }


def test_get_rotation_obj(skale):
    assert skale.node_rotation.get_rotation_obj(DEFAULT_SCHAIN_NAME) == Rotation(
        node_index=0,
        new_node_index=0,
        freeze_until=0,
        rotation_counter=0
    )


def test_get_leaving_history(skale):
    empty = skale.node_rotation.get_leaving_history(DEFAULT_SCHAIN_INDEX)
    assert empty == []
    with mock.patch.object(skale.node_rotation.contract.functions.getLeavingHistory, 'call') \
            as call_mock:
        call_mock.return_value = [(DEFAULT_SCHAIN_ID, 1000), (DEFAULT_SCHAIN_ID, 2000)]
        history = skale.node_rotation.get_leaving_history(DEFAULT_SCHAIN_INDEX)
        assert isinstance(history, list)
        assert history == [
            {
                'id': DEFAULT_SCHAIN_ID,
                'finished_rotation': 1000
            },
            {
                'id': DEFAULT_SCHAIN_ID,
                'finished_rotation': 2000
            }
        ]


def test_is_rotation_in_progress(skale):
    assert skale.node_rotation.is_rotation_in_progress(DEFAULT_SCHAIN_NAME) is False


def test_wait_for_new_node(skale):
    assert skale.node_rotation.wait_for_new_node(DEFAULT_SCHAIN_NAME) is False
