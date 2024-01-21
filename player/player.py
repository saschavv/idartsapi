import json
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def print_communication(response):
    pretty_print_request(response.request)
    pretty_print_response(response)

def pretty_print_request(request):
    log.debug( '\n{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        request.body)
    )

def pretty_print_response(response):
    log.debug('\n{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text)
    ) 

log = logging.getLogger("http")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


base_url = "https://stats.idarts.nl/api/v2"

session = requests.Session() 

login = os.getenv('PLAYERUSER')
password = os.getenv('PLAYERPASSWD')

# Get graphyte info
login_model = {
  'UserName': login,
  "Password": password
}
        
response = session.post(f"{base_url}/token", login_model)
data = response.json()
token = data['Token']

headers = {}
headers['X-ApiKey'] = token
headers['Content-Type'] = 'application/json'

def check_status( response, code ):
    if code == response.status_code:
        print("Correct response code")
    else:
        print(f"Incorrect response code {response.status_code}, expected {code}")

# Get competitions
response = session.get(f"{base_url}/competition", headers=headers)
print_communication(response)

print("-------[ Access Competitions ] ------")
check_status(response, 403)

response = session.get(f"{base_url}/player", headers=headers)
#print_communication(response)
players = response.json()

print("------[ Check access Players ]----- ")
print(f"Number of player recevied {len(players)}")
print_communication(response)


print("------[ Dirk ]----- ")
dirk = next((item for item in players if item["FullName"] == "Dirk van Duijvenbode"), None)
print(json.dumps(dirk, indent=4, sort_keys=True))

player_id = dirk["PlayerId"]
print("------[ Player details ]----- ")
response = session.get(f"{base_url}/player/details?id={player_id}", headers=headers)
print(json.dumps(response.json(), indent=4, sort_keys=True))

print("------[ Last games ]----- ")
response = session.get(f"{base_url}/player/{player_id}/lastmatches", headers=headers)
#print(json.dumps(response.json(), indent=4, sort_keys=True))
matches = response.json()
for match in matches['Matches']:
    context = match['Context']
    p1 = match['PlayerA']['Player']
    p2 = match['PlayerB']['Player']
    r1 = match['ResultA']
    r2 = match['ResultB']
    print(f"> {context['Competition']}-{context['Season']}  {p1['Name']} vs {p2['Name']} = {r1['Score']} - {r2['Score']} Set={match['Set']} Leg={match['Leg']} ")

print("------[ Stats player ]----- ")
response = session.get(f"{base_url}/player/{player_id}/stats", headers=headers)
print(json.dumps(response.json(), indent=4, sort_keys=True))

print("------[ Titles player ]----- ")
response = session.get(f"{base_url}/player/{player_id}/titles", headers=headers)
data  = response.json()
for key in data:
    if 'Count' in key:
        print(f" > {key} - {data[key]}")
