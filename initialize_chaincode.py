from hfc.fabric import Client
from time import sleep
import os

cli = Client(net_profile="test/fixtures/network.json")
org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')

# Create a New Channel, the response should be true if succeed
response = cli.channel_create(
            orderer_name='orderer.example.com',
            channel_name='businesschannel',
            requestor=org1_admin,
            config_yaml='test/fixtures/e2e_cli/',
            channel_profile='TwoOrgsChannel'
            )
print(response==True)

# Join Peers into Channel, the response should be true if succeed
response = cli.channel_join(
               requestor=org1_admin,
               channel_name='businesschannel',
               peer_names=['peer0.org1.example.com',
                           'peer1.org1.example.com'],
               orderer_name='orderer.example.com'
               )
print(response==True)



# Install Chaincode to Peers
# This is only needed if to use the example chaincode inside sdk
gopath_bak = os.environ.get('GOPATH', '')
gopath = os.path.normpath(os.path.join(
                      os.path.dirname(os.path.realpath('__file__')),
                      'test/fixtures/chaincode'
                     ))
os.environ['GOPATH'] = os.path.abspath(gopath)

# The response should be true if succeed
response = cli.chaincode_install(
               requestor=org1_admin,
               peer_names=['peer0.org1.example.com',
                           'peer1.org1.example.com'],
               cc_path='github.com/example_cc_2',
               cc_name='example_cc_2',
               cc_version='v1.0'
               )
print(response==True)

sleep(10)

# Instantiate Chaincode in Channel, the response should be true if succeed
args = ['a', '200', 'b', '300']
response = cli.chaincode_instantiate(
               requestor=org1_admin,
               channel_name='businesschannel',
               peer_names=['peer0.org1.example.com'],
               args=args,
               cc_name='example_cc_2',
               cc_version='v1.0'
               )
print(response==True)
