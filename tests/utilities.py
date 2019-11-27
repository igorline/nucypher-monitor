import os
import random
import string
from unittest.mock import MagicMock

import maya
from constant_sorrow.constants import UNKNOWN_FLEET_STATE
from ipaddress import IPv4Address

from eth_utils.address import to_checksum_address
from nucypher.keystore.keypairs import HostingKeypair


COLORS = ['red', 'green', 'yellow', 'blue', 'black', 'brown', 'purple']


def create_eth_address():
    random_address = to_checksum_address(os.urandom(20))
    return random_address


def create_random_mock_node(generate_certificate: bool = False):
    host = str(IPv4Address(random.getrandbits(32)))
    nickname = ''.join(random.choice(string.ascii_letters) for i in range(25))
    checksum_address = create_eth_address()
    worker_address = create_eth_address()
    timestamp = maya.now().subtract(hours=(random.randrange(0, 10)))
    last_seen = maya.now()

    return create_specific_mock_node(generate_certificate=generate_certificate,
                                     checksum_address=checksum_address,
                                     host=host, nickname=nickname,
                                     worker_address=worker_address,
                                     timestamp=timestamp,
                                     last_seen=last_seen)


def create_node_certificate(host: str, checksum_address: str):
    tls_hosting_keypair = HostingKeypair(host=host,
                                         checksum_address=checksum_address)

    return tls_hosting_keypair.certificate


def create_specific_mock_node(generate_certificate: bool = False,
                              checksum_address: str = '0x123456789',
                              host: str = '127.0.0.1',
                              nickname: str = 'Blue Knight Teal Club',
                              worker_address: str = '0x987654321',
                              timestamp: maya.MayaDT = maya.now().subtract(days=4),
                              last_seen: maya.MayaDT = maya.now(),
                              fleet_state_nickname_metadata=UNKNOWN_FLEET_STATE):
    if generate_certificate:
        # Generate certificate
        certificate = create_node_certificate(host=host, checksum_address=checksum_address)
    else:
        certificate = MagicMock()

    node = MagicMock(certificate=certificate, checksum_address=checksum_address, nickname=nickname,
                     worker_address=worker_address, timestamp=timestamp, last_seen=last_seen,
                     fleet_state_nickname_metadata=fleet_state_nickname_metadata)

    node.rest_url.return_value = f"{host}:9151"

    return node


def convert_node_to_db_row(node):
    return (node.checksum_address, node.rest_url(), node.nickname,
            node.timestamp.iso8601(), node.last_seen.iso8601(), "?")


def verify_mock_node_matches(node, row):
    assert node.checksum_address == row[0], 'staker address matches'
    assert node.rest_url() == row[1], 'rest url matches'
    assert node.nickname == row[2], 'nickname matches'
    assert node.timestamp.iso8601() == row[3], 'new now timestamp matches'
    assert node.last_seen.iso8601() == row[4], 'last seen matches'
    assert "?" == row[5], 'fleet state icon matches'


def create_random_mock_state():
    nickname = ''.join(random.choice(string.ascii_letters) for i in range(25))
    updated = maya.now().subtract(minutes=(random.randrange(0, 59)))
    symbol = random.choice(string.punctuation)
    color_hex = f"#{''.join(random.choice(string.hexdigits) for i in range(6))}"
    color = random.choice(COLORS)

    return create_specific_mock_state(nickname=nickname, symbol=symbol, color_hex=color_hex,
                                      color=color, updated=updated)


def create_specific_mock_state(nickname: str = 'Blue Knight Teal Club',
                               symbol: str = '♣',
                               color_hex: str = '#1E65F3',
                               color: str = 'blue',
                               updated: maya.MayaDT = maya.now()):
    metadata = [(dict(hex=color_hex, color=color), symbol)]
    state = MagicMock(nickname=nickname, metadata=metadata, updated=updated)
    return state


def verify_mock_state_matches(state, row):
    assert state.nickname == row[0], 'nickname matches'
    assert state.metadata[0][1] == row[1], 'symbol matches'
    assert state.metadata[0][0]['hex'] == row[2], 'color hex matches'
    assert state.metadata[0][0]['color'] == row[3], 'color matches'
    assert state.updated.rfc3339() == row[4], 'updated timestamp matches'  # ensure timestamp in rfc3339


def convert_state_to_db_row(state):
    return (state.nickname, state.metadata[0][1], state.metadata[0][0]['hex'],
            state.metadata[0][0]['color'], state.updated.rfc2822())
