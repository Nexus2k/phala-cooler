from substrateinterface import SubstrateInterface

import json
import sys

pool_id = sys.argv[1]

try:
    print("Connecting to substrate node...")
    substrate = SubstrateInterface(
        url="wss://khala.api.onfinality.io/public-ws"
    )
except ConnectionRefusedError:
    print("⚠️ Remote RPC server didn't respond")
    exit()

print("Getting active workers from Pool #%s" % pool_id)
pool_info = substrate.query(
    module='PhalaBasePool',
    storage_function='Pools',
    params=[pool_id]
)
pi_json = json.loads(str(pool_info).replace("'","\""))

calls = []
counter = 1
online_workers = [worker for worker in pi_json["StakePool"]["workers"] if worker not in pi_json["StakePool"]["cd_workers"]]
print("Found %d active workers" % len(online_workers))
for worker in online_workers:
    call ={
        'call_module': 'PhalaStakePoolv2',
        'call_function': 'stop_computing',
        'call_args': {
            'pid': pool_id,
            'worker': worker
        }
    }
    calls.append(call)

batch_call = substrate.compose_call(
    call_module='Utility',
    call_function='batch',
    call_params={
        'calls': calls
    }
)

print("Copy the following output to polkadot.js.org -> Developer -> Extrinsics -> Decode area, then click Submission and sign & submit the transaction with the Pool owner account: ")
print(substrate.encode_scale('Call',batch_call))