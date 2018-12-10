import tester
import requests
from time import sleep

moscow_host = 'http://192.168.99.100:31797'
stpeter_host = 'http://192.168.99.101:32500'

# Create some wallets for test
petya = {'user_id': 'Petya', 'amount': 1000}
vasya = {'user_id': 'Vasya', 'amount': 1000}
vova = {'user_id': 'Vova', 'amount': 1000}
misha = {'user_id': 'Misha', 'amount': 1000}
r = requests.post(moscow_host + '/create_wallet', data = petya, headers={"Host": "wall.e"})
sleep(2)
r = requests.post(moscow_host + '/create_wallet', data = vasya, headers={"Host": "wall.e"})
sleep(2)
r = requests.post(moscow_host + '/create_wallet', data = vova, headers={"Host": "wall.e"})
sleep(2)
r = requests.post(moscow_host + '/create_wallet', data = misha, headers={"Host": "wall.e"})
sleep(2)

# Run all tests from tester module
n=4
tests = ('test_' + str(i+1) for i in range(n))
tests = [getattr(tester, test) for test in tests]
for test in tests:
    if (not test()):
        print('Error on %s' % test.__name__)
        break
    else:
        print('%s passed' % test.__name__)

