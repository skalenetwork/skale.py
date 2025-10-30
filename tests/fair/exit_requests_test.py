#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import pytest


@pytest.mark.parametrize('number_of_nodes', [1])
def test_create_exit_request_and_fetch(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    fair.status.whitelist_node(node_id)
    fair.staking.stake(node_id, value=10_000)

    initial_count = fair.staking.get_my_exit_requests_count()

    fair.staking.request_retrieve(node_id, 1_000)

    new_count = fair.staking.get_my_exit_requests_count()
    assert new_count == initial_count + 1

    my_address = fair.wallet.address
    requests = fair.staking.get_exit_requests_for(my_address)
    assert len(requests) == new_count
    last_request = requests[-1]
    assert last_request.user == my_address
    assert last_request.node_id == node_id
    assert last_request.amount == 1_000
    assert isinstance(last_request.unlock_date, int)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_exit_request_unlock_check(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    fair.status.whitelist_node(node_id)
    fair.staking.stake(node_id, value=10_000)

    fair.staking.request_retrieve(node_id, 500)

    my_address = fair.wallet.address
    request = fair.staking.get_exit_request_at(my_address, 0)
    unlocked_flag = fair.staking.is_request_unlocked(request.request_id)
    assert isinstance(unlocked_flag, bool)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_retrieve_all_request(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    fair.status.whitelist_node(node_id)
    fair.staking.stake(node_id, value=5_000)

    fair.staking.request_retrieve_all(node_id)
    my_address = fair.wallet.address
    count = fair.staking.get_my_exit_requests_count()
    assert count >= 1

    request = fair.staking.get_exit_request_at(my_address, count - 1)
    assert request.amount > 0
