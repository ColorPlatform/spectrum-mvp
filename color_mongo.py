import pymongo
import json
from bson.py3compat import (_unicode)


class ColorMongo:
    """This class looks like MongoDB API, but allows only operations supported in chaincode
    """

    def __init__(self, blockchain_url, database_host, database_name='WALLETSDB', collection_name='wallets'):
        self.__client = pymongo.MongoClient(host='mongodb://' + database_host)
        self.__database = self.__client[database_name]
        self.__collection = self.__database[_unicode(collection_name)]
        self.__updates = []
        self.__inserts = []
        self.__prestate = []
        self.__session = None
        self.__blockchain = Blockchain(blockchain_url)

    def insert_one(self, document):
        # appends documents to list of inserts
        self.__inserts.append(document)
        pass

    def update_one(self, filter, update):
        # appends update command to list of updates
        # TODO Stop when called outside transaction
        # Filtering only supported by "key"
        # Updating is only supported by $set "value"
        # Supported format: updateOne({“key”: “Vasya”}, {“$set”: {“value”: 900}})
        # TODO Check parameters, fail in case of unsupported syntax
        self.__updates.append({"method": "update_one", "filter": filter, "update": update})
        return self.__collection.update_one(filter, update, session=self.__session)

    def find_one(self, filter):
        # appends
        # TODO Stop when called outside transaction
        # TODO Check parameters, fail in case of unsupported syntax
        # Supported format: findOne({“key”: “Petya”})
        result = self.__collection.find_one(filter, session=self.__session)
        self.__prestate.append(result)
        return result

    def start_transaction(self):
        # TODO Stop when called inside transaction
        self.__updates = []
        self.__prestate = []
        self.__session = self.__client.start_session(causal_consistency=False)
        self.__session.start_transaction()
        return self

    def _convert_data(self):
        """Convert data from mongo-related format to chaincode supported format"""
        # commands = [{"key": c["filter"]["key"], "value": c["update"]["$set"]["value"]} for c in self.__updates]
        update_commands = [["wallet", "base_collection", c["filter"]["key"], "value", c["update"]["$set"]["value"]] for c in self.__updates]
        insert_commands = [["wallet", "base_collection", d["key"], key, d[key]] for d in self.__inserts for key in d]
        # insert_commands = [item for sublist in complex_insert_commands for item in sublist]
        commands = insert_commands + update_commands
        # print(commands)
        # TODO Filter out Object ids from prestate
        prestate = [["wallet", "base_collection", d["key"], key, d[key]] for d in self.__prestate for key in d if key != "_id"]

        return {"prestate": prestate, "commands": commands}

    def commit_transaction(self):
        result = self.__blockchain.check_transaction(self._convert_data())
        if not result:
            result = 0
        # We don't want changes will be persisted now in local Mongo, polling is responsible for this.
        self.__session.abort_transaction()
        return result

    def abort_transaction(self):
        self.__session.abort_transaction()
        self.__session.end_session()
        return


class Blockchain:
    def __init__(self, url):
        self.__url = url

    def check_transaction(self, data):
        # TODO Implement when API specification arrives (some data transformation could be needed)
        # HTTP POST /updates {"updates": self.__updates, "prestate": self.__prestate}

        # Now just random wait
        import time
        import random
        from hfc.fabric import Client
        import json

        cli = Client(net_profile="test/fixtures/network-k8s.json")
        org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')
        try:
            print(data)
            response = cli.chaincode_invoke(
                requestor=org1_admin,
                channel_name='businesschannel',
                peer_names=['peer0.org1.example.com'],
                args=[json.dumps(data)],
                cc_name='example_cc_2',
                cc_version='v1.0'
            )
        except Exception as e:
            return -1
