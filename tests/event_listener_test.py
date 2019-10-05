#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE event listener test """

from time import sleep

from unittest import mock

from skale.event_listener import EventListener
import skale.utils.helper as Helper

from tests.utils import generate_random_node_data

CREATED_EVENT_FIELDS = ['nodeIndex', 'owner', 'name', 'ip', 'publicIP',
                        'port', 'nonce', 'time', 'gasSpend']
TEST_EVENT_NAME = 'NodeCreated'


class TestEventListener(object):
    def create_node(self, skale, wallet):
        ip, public_ip, port, name = generate_random_node_data()
        res = skale.manager.create_node(ip, port, name, wallet, public_ip)

        receipt = Helper.await_receipt(skale.web3, res['tx'])
        Helper.check_receipt(receipt)

    def event_handler(self, event):
        self.event_result = event

    def test_event_listener(self, skale, wallet):
        event = skale.nodes.contract.events.NodeCreated
        self.event_result = None
        listener = EventListener(event, self.event_handler, 5)
        listener.run()

        try:
            self.create_node(skale, wallet)

            while not self.event_result:
                sleep(1)

            assert self.event_result.event == TEST_EVENT_NAME
            assert list(self.event_result.args.keys()) == CREATED_EVENT_FIELDS

        finally:
            listener.stop()

    def test_event_listener_filter_params(self, skale, wallet):
        event_mock = mock.Mock()
        create_filter_mock = mock.Mock()
        event_mock.createFilter = create_filter_mock
        event_mock.__name__ = 'EventMock'

        opts = {'fromBlock': 2, 'toBlock': 3,
                'argument_filters': {'arg1': 'value'},
                'topics': []}
        _ = EventListener(event_mock, self.event_handler, 5, filter_opts=opts)
        create_filter_mock.assert_called_with(
            argument_filters={'arg1': 'value'},
            fromBlock=2, toBlock=3, topics=[]
        )
        _ = EventListener(event_mock, self.event_handler, 5)
        create_filter_mock.assert_called_with(fromBlock=1)