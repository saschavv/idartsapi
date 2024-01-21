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
    log.debug(
        "\n{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join("{}: {}".format(k, v) for k, v in request.headers.items()),
            request.body,
        )
    )


def pretty_print_response(response):
    log.debug(
        "\n{}\n{}\n\n{}\n\n{}\n".format(
            "<-----------Response-----------",
            "Status code:" + str(response.status_code),
            "\n".join("{}: {}".format(k, v) for k, v in response.headers.items()),
            response.text,
        )
    )


log = logging.getLogger("http")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


base_url = os.getenv("URL", "https://stats.idarts.nl/api/v2")

session = requests.Session()

token = os.getenv("IDARTSTOKEN")

if not token:
    login = os.getenv("IDARTSUSER")
    password = os.getenv("IDARTSPASSWD")

    login_model = {"UserName": login, "Password": password}

    response = session.post(f"{base_url}/token", login_model)
    data = response.json()
    token = data["Token"]

headers = {}
headers["X-ApiKey"] = token
headers["Content-Type"] = "application/json"


def check_status(response, code):
    if code == response.status_code:
        print("Correct response code")
    else:
        print(f"Incorrect response code {response.status_code}, expected {code}")


year = 2023
tournament_types = [
    "pdc-majors",
    "pdc-world-tour",
    "pdc-euro-tour",
    "pdc-other-tv-tournaments",
    "pdc-global-tours",
    "pdc-youth-major",
]
minimal_status = "Active"

# Get schedule
url = f"{base_url}/schedule/season/{year}"
url += "?tournamentType=" + ",".join(tournament_types)
url += f"&seasonStatus={minimal_status}"
response = session.get(url, headers=headers)
print_communication(response)

print("-------[ Schedule ] ------")
schedule = response.json()
print(json.dumps(schedule, indent=4, sort_keys=True))

print("--- Check schedule --- ")

number_of_seasons = len(schedule["Seasons"])
print(f"Number of seasons {number_of_seasons}")

seasons_in_2024 = [a for a in schedule["Seasons"] if "2024" in a["Name"]]
print("Only season in 2024 starts in 2023")
print(json.dumps(seasons_in_2024, indent=4, sort_keys=True))
