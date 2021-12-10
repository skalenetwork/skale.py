""" SKALE node rotation test """

import mock
import logging

from skale.contracts.manager.node_rotation import Rotation
from skale.utils.contracts_provision.main import (
    add_test2_schain_type, add_test4_schain_type, cleanup_nodes_schains, setup_validator,
    create_nodes, create_schain, _skip_evm_time, add_test_permissions
)
from skale.utils.contracts_provision import (
    D_VALIDATOR_ID, D_VALIDATOR_MIN_DEL, D_DELEGATION_PERIOD, D_DELEGATION_INFO,
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, DEFAULT_NODE_NAME, SECOND_NODE_NAME,
    DEFAULT_SCHAIN_NAME, D_STAKE_MULTIPLIER, INITIAL_DELEGATION_PERIOD, DEFAULT_DOMAIN_NAME
)
from skale.schain_config.generator import get_nodes_for_schain

from skale import Skale
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.contracts_provision import DEFAULT_DOMAIN_NAME
from skale.utils.contracts_provision.utils import generate_random_node_data
from skale.utils.account_tools import send_ether

from tests.constants import (ENDPOINT, TEST_ABI_FILEPATH,
                             TEST_ALLOCATOR_ABI_FILEPATH,
                             ETH_PRIVATE_KEY)

logger = logging.getLogger(__name__)

TEST_ETH_AMOUNT = 1


TEST_VERIFICATION_VECTORS = [
        [
            {
                'x': {
                    'a': "0x1e6e075338ec8cf604af22511625d5f9b184b462844fd0ccf301a198f5cb12a2",
                    'b': "0x1b85c72c39aa376df512ba5217376ec90c2492945a86139a136b35ff616f921e"
                },
                'y': {
                    'a': "0x174265c0fc2ce359084b239ad9b703441998df7fee298741e52c2175a4a4adb2",
                    'b': "0x0a1cd10cadd730b54ff21aed30be2dbdb315afe48b3d01c36a5301b0587c9350"
                }
            },
            {
                'x': {
                    'a': "0x29b361184395f6fc0116eb3a6f7d7ebde8f30c6606d78d389fe1eea772057f59",
                    'b': "0x0f51d5bfbfba84a92eab561f5c27ae31aef5f9231f64a416b4193a3026bd42c9"
                },
                'y': {
                    'a': "0x2192c321f3856ccf0d75c1d705b06fce6839feffd8a08ca50999a6ac480039a5",
                    'b': "0x20e656db446c12ad9ea7430d62d54491aae1b72bbf545a89ac1b8f64ef44fb65"
                }
            },
            {
                'x': {
                    'a': "0x272f9995e067c924c4972f0987dcf18a8ce8c53364306cf5dca58eaf0875ac6c",
                    'b': "0x0635b7c445eb73dd5631b8a9b43db49e64e53a12f99977a6c42c575056c95122"
                },
                'y': {
                    'a': "0x094c75cc853d4850b8ef04cef73de0fa2910c247d7575a326395e53dee2f857a",
                    'b': "0x1577eac1bd673048afd017c4775c9f961bb3a2bb3181e2774ad8d57c770cc63d"
                }
            }
        ],
        [
            {
                'x': {
                    'a': "0x2a2fe9290dac9173bf403b7eb84dfe2e1779692c69a249f880e71df2308d6b02",
                    'b': "0x0c6b3fc6d4f54d5a8f47d8df1000563e7978e6e8ad79969db5d7fe5fe9b768ab"
                },
                'y': {
                    'a': "0x1231f93c5c14c530478e19a56e4bf0fca86ce081f79ff170d2c365bbe3e13c61",
                    'b': "0x06f3728f4bdb694ef68225224e1c1c60eaf095a9da784e433aecce28b01004d0"
                }
            },
            {
                'x': {
                    'a': "0x0b6392a2de9a8e405474a862889cc203b85cf10ce38369ce9b02ead40c284b6f",
                    'b': "0x108f7e0d02067afe6db52a6e51928abc3854794b73cb0949028f06ee9bc9b712"
                },
                'y': {
                    'a': "0x0859827216ecfdedd71809b4a54c04870d977be3fcad999013546eefb988b5c7",
                    'b': "0x121f228703cd90e0c3726b7b5a87338f9237f91c17ab2e80751c454821bb43d9"
                }
            },
            {
                'x': {
                    'a': "0x11feed899ef9145736d7a2d1a2cdb99a5fe529b6112e42ca6cd892f1c90efa8d",
                    'b': "0x2b286caa9a04b668b28ec93a8831a076e89c5b892c0c731f04a2f2a5c9e89cb7"
                },
                'y': {
                    'a': "0x209566e066a390b2f213b3dadd17d3c3e11cd6323651490d3774b41284e104d0",
                    'b': "0x199627b30b2f8b3906712c5d19c98b68ed8fcb25804522cd4dc31aeb897a9a74"
                }
            }
        ],
        [
            {
                'x': {
                    'a': "0x82977d3decd6310d7c6b88fb199793d75a24a30c5360c19629bc894d987ebc7",
                    'b': "0x25965fba3727d9b4348e4282cb97a36f3d278bd7f50c38d643cfb3787f125de6"
                },
                'y': {
                    'a': "0xa41b22d0f1155e18b2ddf9402bbeb87f2c3a3eb68d044040a24d655c6a2f765",
                    'b': "0x3b8b2e2e5e07e531a42cbf7606eed379935c181502204650a6e896f5abcefe6"
                }
            },
            {
                'x': {
                    'a': "0x171d38b88b0c21cab623feff824672a473491dddd2799bbc2fa15f38db3266c8",
                    'b': "0xe4341d9612c4083e0fa8288c858fa3002ecf731569adcbaaf2eb1096b9d9ff5"
                },
                'y': {
                    'a': "0x580a8febdb45defa6082939dfe18d7db972bd2604e876c025480282ff55de51",
                    'b': "0x2cd819a133cfd7928489691e5d8beeb523fe8c85faa92ef9526b7aa025602b4a"
                }
            },
            {
                'x': {
                    'a': "0x2801d3f4e9d428b8a15cb55d785b38e23ebbea113172fa9711ce605d461b6cfd",
                    'b': "0x272cd25c63150d48b7cdf76e9afd4f092cc7aeb9b496ee54099139498ac60d66"
                },
                'y': {
                    'a': "0x239c34d400f69eaa1d0161248da69ff4cedd9bf471367528a2092ad3bda8a351",
                    'b': "0x25bd47bcdd4b7ecd6aeacd592b1ba3ccf60dcae9d929ec4cd1c460802fb204af"
                }
            }
        ],
        [
            {
                'x': {
                    'a': "0x28b25a69fde6566272ea92f41d6e466260376bc5f38d92f606536810d9c26546",
                    'b': "0x13e561299bb7ec35a76ae7f18d16446dd34a35fc2c42adff4823db4bda3e3c3d"
                },
                'y': {
                    'a': "0x1ab82d04b3c58cb942bf31a63b39903c4f28ba565fc8f2b2dd1f649e2204fd3f",
                    'b': "0x1fc8a151380f59a44b6139561608f1f53ef24d3272c895243d609cdba3d95f3e"
                }
            },
            {
                'x': {
                    'a': "0x318315358286c97dc122e81b7eb6a49843d2127b0450d8eeffdd43150020bf1",
                    'b': "0x1b90e5143511db72b023c3e6179ec822ae162e9deaa3f4b631c67d564deda696"
                },
                'y': {
                    'a': "0x22c94cf52a06eeb1e1dbf191a99cbf0c30890ec79f17b8703337e2effe1139c",
                    'b': "0x27c9137635c07fa316cdd4c21fc1a4072353ac8b75fbb9ef5e1f7612bd5e6631"
                }
            },
            {
                'x': {
                    'a': "0x147c80f22bd325b3b103747d96602928b19bfc070ebd5d84bb1581539a6dce1a",
                    'b': "0x2dd5ddbf3f8565b8c95d3ea70f328f73f1e536e4f1e0cc59f24b35b9bdede74c"
                },
                'y': {
                    'a': "0xa2148b6dcf01f00420101d8798cb6a2bcd9dc7629054f79a8f0271efaac2c01",
                    'b': "0x9a3750811006d59670fbee24789f63f2c695aff7daf3eb159585ff8b9b6e583"
                }
            }
        ]
    ]



TEST_ENCRYPTED_SECRET_KEY_CONTRIBUTIONS =  [
        [
            {
                "share": "0x74997044fc0dbf8d6ad2c3db6d6f78e650fdcffd82d02b7bcd37d4c1e817f320",
                "publicKey": [
                    "0x5b6c340aa86f9f53a3dd19c3fc4e2c1be048741f35c41763d063a30d32e94837",
                    "0x0794e6ca938e325bb800f6c5685993af21b13d6dd2e3cefa28ed136f3e713096"
                ]
            },
            {
                "share": "0x946de8c332bf822b6bf15b6c7f6b859a5247a46fb20495c6a65b0baabfddf09c",
                "publicKey": [
                    "0x8fb6aba303d3254d5e147a99e2d049e71823e8ce0c7b874efed65c6cf59541b2",
                    "0x2a369d48e36f0486628229f7a42d2a8b92ee8f2ec3477e82fcf6044e57a57005"
                ]
            },
            {
                "share": "0xb4996277b8e20b324bb45ac31593ddd7ea693841a6283e0de663a2a25210dc63",
                "publicKey": [
                    "0x55074e2b548133b240c717673b87301b118efbb474c72264bab4c7135aaf964e",
                    "0x65e5cf0e3e20ccd9e8b41eb3fa1e2fb3aaa3e688871799092b2c146aaa9d910b"
                ]
            },
            {
                "share": "0x99f5a75616814b6b637397ab2365eefd83dff8ed1281f267508eebbf58b1fdcc",
                "publicKey": [
                    "0x09cdc126ab08d0d99be19e8205b360a7de0f5528eef5a313bf89dce90dcd8226",
                    "0xf35052c93b992c41586c8fa84f0d15a9b07a0bf150b36ba831895e589fe4bb58"
                ]
            }
        ],
        [
            {
                "share": "0xf06f04c5e4b809a4d44b717859fcbb65617638447c98cf7fb4a4d83e3e9dc940",
                "publicKey": [
                    "0xe5d3623fe57d1061df44bc86d24afea5035f0cfe7d3618c04eaf93aad83c0524",
                    "0x4459af9a1945cdc75311f388291c71ed424972225bfe51fefd65f1d16947efa9"
                ]
            },
            {
                "share": "0xd35666da0bf83406863a80bd7f9d38768e67f1f83062419b7c14736a0a98291a",
                "publicKey": [
                    "0x7212a1a34a4d9fd123e5ee17f4e29ecd0ae77efe043feff106d5e96c19fcae8f",
                    "0x296eff026a8491ed17ea2ceac08faa4e923b42b683279c2f0c39a1671ada1057"
                ]
            },
            {
                "share": "0xc33ef8baf18cf3f09f656cdb6d5012f1489862df7afbe9a4291838eb889ccf93",
                "publicKey": [
                    "0x982d5b6dcbb63463b45552ea6769bd7c320cf5e3be542dad6c2afca073754650",
                    "0xa3d97ce152037112a68fe1caa165787760c847e8d62fd0884ba4ef306a91cb36"
                ]
            },
            {
                "share": "0x49cf197d8cdf5ddcbf10abac8fe603139842789f8eca9f967eb4a2b253ad7c08",
                "publicKey": [
                    "0x2a8db369ff7068df6f97831f4278d4c0d8c51c9fd2a1a424df1adbe44021371c",
                    "0x16eec1a222bfa1735ea569b2547c5f1929face9c3db75c046aceb34b09f2c6de"
                ]
            }
        ],
        [
            {
                "share": "0xa4fb06c39f1c614f39ef3c3647d9f65b5f881489f822b7551d88c504060eaa50",
                "publicKey": [
                    "0x14b44bf482f62a4451e01bfbd44d504994ecd1fd6852bffa30ce1d22aebe5a4b",
                    "0x8cd1f57f0b75e8aeec3cdc900aa206e66877d346514e52041d190ebd3cbdf6f8"
                ]
            },
            {
                "share": "0xa7ebaee6cd94de57e1967d1146cbc87f44a90c992af1fbe5ef74d20c779169ce",
                "publicKey": [
                    "0xa3bdf65c98fa52489c80a07b5ed6a938714cb24ae27d6f17a90006d1a061b2df",
                    "0x82fa92efe21dc1a5f113d50734c7c7a163d4ff335d8b3adf69cd3be2a31edc5e"
                ]
            },
            {
                "share": "0x0d6fdbf63f62b4dc620c53c86cdfb39fc3a2767a02b83bd7b36bc580ab7a8b2e",
                "publicKey": [
                    "0x4873209fba96e37b36ca0bd79d8aeb4ff70dd2b036760727abe872fa045f99a5",
                    "0xe7de3dd4b6cefca8c0eb1ca0329aa1abb88712aa88243c631f34b79a2514adff"
                ]
            },
            {
                "share": "0x56a97c8d534ec59f4a66a1183a2c50876dff56cea8da87e9da67e7e60934664d",
                "publicKey": [
                    "0x7b101d3fdd35682cc130cdd38275f4af7f5ced203e626645de3c06bb6cbe7c51",
                    "0xa24c9bec58f52d77bf02255ffd269531510657001c594d49f57f72b683c9f9d8"
                ]
            }
        ],
        [
            {
                "share": "0xc4c9b7d2c103e2e6ae6eabad2f8cc4689b609ed9a383fbef4631283b69dcb6d8",
                "publicKey": [
                    "0x83d4786b778b7205bd4552164032fc450af8a113605447e37f1377220be94757",
                    "0x9d684b47e011436a75a3461bc358cd7cddb903c5ca5e6e9e6bf3fb968262615e"
                ]
            },
            {
                "share": "0x81741c178c9109af1b8877b45e3e85b62a7c85c21435805a1ddb08fab3a98569",
                "publicKey": [
                    "0x8e187ff2e9d6110c15e0ec0cf2729c73fc1015d58fb3e8df8d3bef736c68cb1c",
                    "0xa8f04b03ce29735c88f006b22a6311c403f2cc4f0227614796da034b9bf887b3"
                ]
            },
            {
                "share": "0xe1a7e43508a3d827cc614ad891e704652d07fff8813f98098d1764e0815afa79",
                "publicKey": [
                    "0x90470f72b785d0b908830d34939a81257c396bc3031c8fd9de66f8e614a9ea0e",
                    "0x035d4b630d0196df057c8fd9441f3d71a6f29e73aabf3c205936ac66473dd437"
                ]
            },
            {
                "share": "0xabc88f11ab7183250d64bd11dcd5d06f9959bff61f88dd4670f01e8e7ca8a2db",
                "publicKey": [
                    "0x2d9547bbce4df3c5f822b8c353a5e36916f28325918f6db7336bce285d1da45f",
                    "0x3444c74b8d193e782d8ff9947a203277189f559d4e03b10fc30d7c468d0f55e5"
                ]
            }
        ]
    ]


def generate_web3_wallets(web3, n_of_keys):
    logger.info(f'Generating {n_of_keys} test wallets')
    return [
        generate_wallet(web3)
        for _ in range(n_of_keys)
    ]


def transfer_eth_to_wallets(skale, wallets):
    logger.info(
        f'Transfering {TEST_ETH_AMOUNT} ETH to {len(wallets)} test wallets'
    )
    for wallet in wallets:
        send_ether(skale.web3, skale.wallet, wallet.address, TEST_ETH_AMOUNT)


def link_addresses_to_validator(skale, wallets):
    logger.info('Linking addresses to validator')
    for wallet in wallets:
        link_node_address(skale, wallet)


def link_node_address(skale, wallet):
    validator_id = skale.validator_service.validator_id_by_address(
        skale.wallet.address)
    main_wallet = skale.wallet
    skale.wallet = wallet
    signature = skale.validator_service.get_link_node_signature(
        validator_id=validator_id
    )
    skale.wallet = main_wallet
    skale.validator_service.link_node_address(
        node_address=wallet.address,
        signature=signature,
        wait_for=True
    )


def set_up_nodes(skale, nodes_number):
    wallets = generate_web3_wallets(skale.web3, nodes_number)
    transfer_eth_to_wallets(skale, wallets)
    link_addresses_to_validator(skale, wallets)
    skale_instances = [init_skale_from_wallet(wallet) for wallet in wallets]
    nodes_data = register_nodes(skale_instances)
    return nodes_data, skale_instances


def register_node(skale):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    skale.manager.create_node(
        ip=ip,
        port=port,
        name=name,
        public_ip=public_ip,
        domain_name=DEFAULT_DOMAIN_NAME,
        wait_for=True
    )
    node_id = skale.nodes.node_name_to_index(name)
    logger.info(f'Registered node {name}, ID: {node_id}')
    return {
        'node': skale.nodes.get_by_name(name),
        'node_id': node_id,
        'wallet': skale.wallet
    }


def register_nodes(skale_instances):
    nodes = [
        register_node(sk)
        for sk in skale_instances
    ]
    return nodes



def init_skale_from_wallet(wallet) -> Skale:
    return Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)


def send_broadcasts(nodes, skale_instances, group_index):
    for i, node in enumerate(nodes):
        res = skale_instances[i].dkg.broadcast(
            group_index,
            i,
            TEST_VERIFICATION_VECTORS[i],
            TEST_ENCRYPTED_SECRET_KEY_CONTRIBUTIONS[i]
        )
        print('i')
        print(i)
        print(node)
        print(res)


def test_rotation_history(skale):
    cleanup_nodes_schains(skale)
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    name = create_schain(skale, random_name=True)
    schain = skale.schains.get_by_name(name)
    nodes_in_chain = get_nodes_for_schain(skale, name)

    group_index = skale.web3.sha3(text=name)
    group_index_str = skale.web3.toHex(group_index)

    print(schain)
    print(nodes_in_chain)

    send_broadcasts(nodes, skale_instances, group_index)

    assert False

    # 0. cleanup all nodes + chains
    # 1. create 4 nodes
    # 2. create schain on them
    # 3. complete dkg on all of them
    # 4. create node 5
    # 5. do node exit
    # 6. check out node history

    # skale.node_rotation.