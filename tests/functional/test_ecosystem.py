from ape_beacon.containers import BeaconExecutionPayload

# NOTE: testing success cases given time constraints
# TODO: testing non-success
# TODO: better testing around expect, particuarly on data truncation with len()


def test_decode_block_when_no_payload(beacon):
    signed_block_resp_with_no_payload = {
        "version": "phase0",
        "execution_optimistic": False,
        "data": {
            "message": {
                "slot": "1",
                "proposer_index": "61090",
                "parent_root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",
                "state_root": "0x7773ed5a7e944c6238cd0a5c32170663ef2be9efc594fb43ad0f07ecf4c09d2b",
                "body": {
                    "randao_reveal": "0x8e245a52a0a680fcfe789013e123880c321f237de10cad108dc55dd47290d7cfe50cdaa003c6f783405efdac48cef44e152493abba40d9f9815a060dd6151cb0635906c9e3c1ad4859cada73ccd2d6b8747e4aeeada7d75d454bcc8672afa813",  # noqa: E501
                    "eth1_data": {
                        "deposit_root": "0x4e910ac762815c13e316e72506141f5b6b441d58af8e0a049cd3341c25728752",  # noqa: E501
                        "deposit_count": "100596",
                        "block_hash": "0x89cb78044843805fb4dab8abd743fc96c2b8e955c58f9b7224d468d85ef57130",  # noqa: E501
                    },
                    "graffiti": "0x74656b752f76302e31322e31342b34342d673863656562663600000000000000",  # noqa: E501
                    "proposer_slashings": [],
                    "attester_slashings": [],
                    "attestations": [
                        {
                            "aggregation_bits": "0x0080020004000000008208000102000905",
                            "data": {
                                "slot": "0",
                                "index": "7",
                                "beacon_block_root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",  # noqa: E501
                                "source": {
                                    "epoch": "0",
                                    "root": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                                "target": {
                                    "epoch": "0",
                                    "root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",  # noqa: E501
                                },
                            },
                            "signature": "0x967dd2946358db7e426ed19d4576bc75123520ef6a489ca50002222070ee4611f9cef394e5e3071236a93b825f18a4ad07f1d5a1405e6c984f1d71e03f535d13a2156d6ba22cb0c2b148df23a7b8a7293315d6e74b9a26b64283e8393f2ad4c5",  # noqa: E501
                        }
                    ],
                    "deposits": [],
                    "voluntary_exits": [],
                },
            },
            "signature": "0xa30d70b3e62ff776fe97f7f8b3472194af66849238a958880510e698ec3b8a470916680b1a82f9d4753c023153fbe6db10c464ac532c1c9c8919adb242b05ef7152ba3e6cd08b730eac2154b9802203ead6079c8dfb87f1e900595e6c00b4a9a",  # noqa: E501
        },
    }
    block_data_with_none_payload = signed_block_resp_with_no_payload["data"]["message"]
    actual = beacon.decode_block(block_data_with_none_payload)
    assert actual.body.execution_payload is None


def test_decode_block_when_payload(beacon, ethereum):
    # SEE: https://github.com/ethereum/consensus-specs/blob/dev/specs/bellatrix/beacon-chain.md#beaconblockbody  # noqa: E501
    signed_block_resp = {
        "version": "phase0",
        "execution_optimistic": False,
        "data": {
            "message": {
                "slot": "1",
                "proposer_index": "61090",
                "parent_root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",
                "state_root": "0x7773ed5a7e944c6238cd0a5c32170663ef2be9efc594fb43ad0f07ecf4c09d2b",
                "body": {
                    "randao_reveal": "0x8e245a52a0a680fcfe789013e123880c321f237de10cad108dc55dd47290d7cfe50cdaa003c6f783405efdac48cef44e152493abba40d9f9815a060dd6151cb0635906c9e3c1ad4859cada73ccd2d6b8747e4aeeada7d75d454bcc8672afa813",  # noqa: E501
                    "eth1_data": {
                        "deposit_root": "0x4e910ac762815c13e316e72506141f5b6b441d58af8e0a049cd3341c25728752",  # noqa: E501
                        "deposit_count": "100596",
                        "block_hash": "0x89cb78044843805fb4dab8abd743fc96c2b8e955c58f9b7224d468d85ef57130",  # noqa: E501
                    },
                    "graffiti": "0x74656b752f76302e31322e31342b34342d673863656562663600000000000000",  # noqa: E501
                    "proposer_slashings": [],
                    "attester_slashings": [],
                    "attestations": [
                        {
                            "aggregation_bits": "0x0080020004000000008208000102000905",
                            "data": {
                                "slot": "0",
                                "index": "7",
                                "beacon_block_root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",  # noqa: E501
                                "source": {
                                    "epoch": "0",
                                    "root": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                                "target": {
                                    "epoch": "0",
                                    "root": "0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87",  # noqa: E501
                                },
                            },
                            "signature": "0x967dd2946358db7e426ed19d4576bc75123520ef6a489ca50002222070ee4611f9cef394e5e3071236a93b825f18a4ad07f1d5a1405e6c984f1d71e03f535d13a2156d6ba22cb0c2b148df23a7b8a7293315d6e74b9a26b64283e8393f2ad4c5",  # noqa: E501
                        }
                    ],
                    "deposits": [],
                    "voluntary_exits": [],
                    "execution_payload": {
                        "parent_hash": "0xcb94e150c06faee9ab2bf12a40b0937ac9eab1879c733ebe3249aafbba2f80b1",  # noqa: E501
                        "fee_recipient": "0x",
                        "state_root": "0x8728474146565003152f9cee496de043fd68566dabdb06116a0d5bfc63e1a5a9",  # noqa: E501
                        "receipts_root": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",  # noqa: E501
                        "logs_bloom": "0x0",
                        "prev_randao": "0x6474a9820165be467f1d25ed54f4802f72c4c95a19cf4ba4cdb8894f55d74195",  # noqa: E501
                        "block_number": "15796864",
                        "gas_limit": "30000000",
                        "gas_used": "12900335",
                        "timestamp": "1660932629",
                        "total_difficulty": "58750003716598352816469",
                        "extra_data": "0x",
                        "base_fee": "30487386013",
                        "block_hash": "0xcb94e150c06faee9ab2bf12a40b0937ac9eab1879c733ebe3249aafbba2f80b1",  # noqa: E501
                        "transactions": [],
                    },
                },
            },
            "signature": "0xa30d70b3e62ff776fe97f7f8b3472194af66849238a958880510e698ec3b8a470916680b1a82f9d4753c023153fbe6db10c464ac532c1c9c8919adb242b05ef7152ba3e6cd08b730eac2154b9802203ead6079c8dfb87f1e900595e6c00b4a9a",  # noqa: E501
        },
    }
    block_data = signed_block_resp["data"]["message"]
    payload_data = block_data["body"]["execution_payload"]
    prev_randao_data = block_data["body"]["execution_payload"]["prev_randao"]

    actual = beacon.decode_block(block_data)
    assert actual is not None

    expected_payload_data = ethereum.decode_block(payload_data).dict()
    expected_payload_data.update({"prev_randao": prev_randao_data})
    expected_payload = BeaconExecutionPayload.parse_obj(expected_payload_data)

    actual_payload = actual.body.execution_payload
    assert actual_payload == expected_payload
