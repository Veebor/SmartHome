import requests
import json
r1 = requests.get('http://localhost:3000/login/test/test')
text = str(r1.text)
response = json.loads(text)
token = response['token']
r2 = requests.get('http://localhost:3000/' + token + '/home')
text2 = str(r2.text)
response2 = json.loads(text2)
status2 = response2['status']
if status2 == 'OK':
    print('Test passed')
    exit(0)
else:
    print('Error')
    exit(1)
