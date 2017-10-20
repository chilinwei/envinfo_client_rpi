import requests,uuid

def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac

data = {
        'ts': "20170912133728976539",
        'ax': "50",
        'ay': "50",
        'az': "50",
        'light': "50",
        'temp': "50",
        'humi': "50",
        'volts': "50"
    }

# get mac for uid
uid = get_mac_address()

r = requests.post('http://localhost:8080/addenvdata/%s'%uid, json=data)
print(r)