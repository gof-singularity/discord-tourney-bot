from pydoc import resolve
import requests
import json
headers={
    'Content-type':'application/json', 
    'Accept':'application/json'
}

string = {
   "name":"mal1231231231231",
   "type":"round robin",
   "rankedBy":"points scored",
   "startAt":"2022-06-22T03:00:00"
}
#obj = json.loads(string)
print(string)
response = requests.post('http://localhost:8080/tournament/create', json=string, headers=headers)
print(response.text)