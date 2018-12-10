from hfc.fabric import Client
from time import sleep
import pymongo
from bson.py3compat import (_unicode)

database_host = "mongo:27017"
# cli = Client(net_profile="test/fixtures/network.json")
cli = Client(net_profile="test/fixtures/network-k8s.json")
org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')
client = pymongo.MongoClient(host='mongodb://' + database_host)
database = client["WALLETSDB"]
collection = database[_unicode("wallets")]
flag = True
while flag:
    response = cli.query_info(
                   requestor=org1_admin,
                   channel_name='businesschannel',
                   peer_names=['peer0.org1.example.com', 'peer1.org1.example.com'],
                   )

    answer = collection.find_one({"key": "secret_key_for_polling"})
    if not answer:
        collection.insert_one({'key': "secret_key_for_polling",'value': 2})
        answer = collection.find_one({"key": "secret_key_for_polling"})
    for i in range(answer["value"], response.height):
        response = cli.query_block(
            requestor=org1_admin,
            channel_name='businesschannel',
            peer_names=['peer0.org1.example.com'],
            block_number=str(i)
        )

        response_inner = cli.query_block_by_txid(
            requestor=org1_admin,
            channel_name='businesschannel',
            peer_names=['peer0.org1.example.com'],
            tx_id=response['data']['data'][0]['payload']['header']['channel_header']['tx_id']
        )
        commands = response_inner['data']['data'][0]['payload']['data']['actions'][0]['payload']['action']['proposal_response_payload']['extension']['results']['ns_rwset'][0]['rwset']['writes']
        doc_dict = {}
        for command in commands:
            key = command["key"]
            key_list = key.split("\x00")
            if not doc_dict.get(key_list[4]):
                doc_dict[key_list[4]] = {"key": key_list[4]}
                doc_dict[key_list[4]][key_list[5]] = command["value"].decode()
            else:
                doc_dict[key_list[4]][key_list[5]] = command["value"].decode()
        docs = [doc_dict[key] for key in doc_dict]
        session = client.start_session(causal_consistency=True)
        session.start_transaction()
        for document in docs:
            if not document.get("key"):
                continue
            collection.update_one({"key": document["key"]}, {"$set": document}, upsert=True)
        collection.update_one({'key': "secret_key_for_polling"}, {"$set": {'value': i+1}})
        session.commit_transaction()
    sleep(0.1)
