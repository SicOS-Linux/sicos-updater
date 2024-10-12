import os
import json
import requests
import time
import getpass

# Get the username
username = getpass.getuser()

# Set the API endpoint and local file path
endpoint = "http://cliente.tomadahost.cloud:10060/update"
updatesh_endpoint = "http://cliente.tomadahost.cloud:10060/updatesh"
local_file_path = f"/home/{username}/.update/POINTRELEASE.json"

# Set the default value for pointRelease
default_point_release = 1

# Initialize the pointRelease value
if os.path.exists(local_file_path):
    with open(local_file_path, 'r') as f:
        point_release = json.load(f)['pointRelease']
else:
    point_release = default_point_release
    with open(local_file_path, 'w') as f:
        json.dump({'pointRelease': point_release}, f)

# Send a GET request to the endpoint
response = requests.get(endpoint)
response_json = response.json()

# Check if the pointRelease values match
if point_release == response_json['pointRelease']:
    print("No update available.")
else:
    print("Update available, downloading and executing script...")
    # Send a GET request to the updatesh endpoint
    updatesh_response = requests.get(updatesh_endpoint)
    script = updatesh_response.text

    # Execute the script as root
    os.system(f"sudo gbs -c '{script}'")

    # Update the local pointRelease value
    point_release = response_json['pointRelease']
    with open(local_file_path, 'w') as f:
        json.dump({'pointRelease': point_release}, f)
