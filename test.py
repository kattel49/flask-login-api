import requests

base = 'max'

user_data = []
tokens = []

for i in range(10):
    user = base + chr(97+i)
    
    user_data.append({"username": user, "password" : user})

    data = requests.post("http://127.0.0.1:5000/register", json=user_data[i])
    print(data.json())

    data = requests.post("http://localhost:5000/login", json=user_data[i])
    token = data.json()['data']['token']
    tokens.append(token)

for token in tokens:
    print(token)

for i in range(2):
    data = requests.get("http://localhost:5000/users", headers={"Authorization": "Bearer " + tokens[i]})
    print(data.json())