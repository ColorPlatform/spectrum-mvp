import requests
from time import sleep
import json


moscow_host = 'http://192.168.99.100:31324'
stpeter_host = 'http://192.168.99.101:31320'


def test_1():
    # Transfer
    transfer = {'from_user_id': 'Vasya', 'to_user_id': 'Petya', 'amount': 100}
    r = requests.post(moscow_host + '/transfer', data = transfer, headers={"Host": "wall.e"})
    sleep(5)
    print(r.text)
    check = (json.loads(r.text)['balance'] == 900)
    if (not check):
        return 0

    # Check
    r = requests.get(moscow_host + '/account/Petya', headers={"Host": "wall.e"})
    check = (json.loads(r.text)['value'] == '1100')
    print(r.text)
    if (not check):
        return 0    

    # Roll back
    transfer = {'from_user_id': 'Petya', 'to_user_id': 'Vasya', 'amount': 100}
    r = requests.post(moscow_host + '/transfer', data = transfer, headers={"Host": "wall.e"})
    sleep(5)

    return 1


def test_2():
    # Transfer
    transfer = {'from_user_id': 'Vasya', 'to_user_id': 'Petya', 'amount': 100}
    r = requests.post(moscow_host + '/transfer', data = transfer, headers={"Host": "wall.e"})
    sleep(5)
    print(r.text)
    check = (json.loads(r.text)['balance'] == 900)
    if (not check):
        return 0

    # Check
    r = requests.get(stpeter_host + '/account/Petya', headers={"Host": "wall.e"})
    print(r.text)
    check = (json.loads(r.text)['value'] == '1100')
    if (not check):
        return 0    

    # Roll back
    transfer = {'from_user_id': 'Petya', 'to_user_id': 'Vasya', 'amount': 100}
    r = requests.post(moscow_host + '/transfer', data = transfer, headers={"Host": "wall.e"})
    sleep(5)

    return 1


def test_3():
    # Transfer

    r1 = requests.post(moscow_host + '/transfer', data={'from_user_id': 'Vasya', 'to_user_id': 'Petya', 'amount': 1000},
                       headers={"Host": "wall.e"})
    r2 = requests.post(stpeter_host + '/transfer', data={'from_user_id': 'Vasya', 'to_user_id': 'Vova', 'amount': 1000},
                       headers={"Host": "wall.e"})
    sleep(20)
    ress = [r1, r2]
    print(r1.text)
    print(r2.text)

    # Check
    r1 = requests.get(moscow_host + '/account/Vasya', headers={"Host": "wall.e"})
    r2 = requests.get(moscow_host + '/account/Petya', headers={"Host": "wall.e"})
    r3 = requests.get(moscow_host + '/account/Vova', headers={"Host": "wall.e"})
    # ress = grequests.map(reqs)
    print(r1.text)
    print(r2.text)
    print(r3.text)
    ress = [r1, r2, r3]
    check = (json.loads(ress[0].text)['value'] == '0')
    if (not check):
        print(ress[0].text)
        return 0
    check = ((json.loads(ress[1].text)['value'] == '2000') & (json.loads(ress[2].text)['value'] == '1000') |
                (json.loads(ress[1].text)['value'] == '1000') & (json.loads(ress[2].text)['value'] == '2000'))
    if (not check):
        print(ress[1].text)
        print(ress[2].text)
        return 0
    sleep(10)
    
    # Roll back
    if (json.loads(ress[1].text)['value'] == '2000'):
        r = requests.post(moscow_host + '/transfer', data = {'from_user_id': 'Petya', 'to_user_id': 'Vasya', 'amount': 1000}, headers={"Host": "wall.e"})
    else:
        r = requests.post(moscow_host + '/transfer', data = {'from_user_id': 'Vova', 'to_user_id': 'Vasya', 'amount': 1000}, headers={"Host": "wall.e"})
    sleep(8)
    return 1


def test_4():
    # Transfer

    r1 = requests.post(moscow_host + '/transfer', data={'from_user_id': 'Vasya', 'to_user_id': 'Petya', 'amount': 100},
                       headers={"Host": "wall.e"})
    sleep(5)
    r2 = requests.post(stpeter_host + '/transfer', data={'from_user_id': 'Vova', 'to_user_id': 'Misha', 'amount': 100},
                       headers={"Host": "wall.e"})
    ress = [r1, r2]
    print(r1.text)
    print(r2.text)

    # Check
    check = (json.loads(ress[0].text)['balance'] == 900) & (json.loads(ress[1].text)['balance'] == 900)
    if (not check):
        return 0
    sleep(10)


    r1 = requests.get(moscow_host + '/account/Petya', headers={"Host": "wall.e"})
    r2 = requests.get(moscow_host + '/account/Misha', headers={"Host": "wall.e"})

    ress = [r1, r2]
    print(ress[0].text)
    print(ress[1].text)
    check = (json.loads(ress[0].text)['value'] == '1100') & (json.loads(ress[1].text)['value'] == '1100')
    if (not check):
        return 0

    # Roll back
    requests.post(moscow_host + '/transfer', data = {'from_user_id': 'Petya', 'to_user_id': 'Vasya', 'amount': 100}, headers={"Host": "wall.e"})
    requests.post(moscow_host + '/transfer', data = {'from_user_id': 'Misha', 'to_user_id': 'Vova', 'amount': 100}, headers={"Host": "wall.e"})

    return 1    
