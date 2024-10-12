import os
import json
import requests
import getpass

def get_username():
    return getpass.getuser()

def get_local_file_path(username):
    return f"/home/{username}/.update/POINTRELEASE.json"

def get_default_point_release():
    return 1

def initialize_point_release(local_file_path, default_point_release):
    if os.path.exists(local_file_path):
        with open(local_file_path, 'r') as f:
            return json.load(f)['pointRelease']
    else:
        point_release = default_point_release
        with open(local_file_path, 'w') as f:
            json.dump({'pointRelease': point_release}, f)
        return point_release

def send_get_request(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing endpoint: {e}")
        return None

def execute_script_as_root(script):
    try:
        os.system(f"sudo gbs -c '{script}'")
    except Exception as e:
        print(f"Error executing script: {e}")

def update_local_point_release(local_file_path, point_release):
    with open(local_file_path, 'w') as f:
        json.dump({'pointRelease': point_release}, f)

def main():
    username = get_username()
    local_file_path = get_local_file_path(username)
    default_point_release = get_default_point_release()
    point_release = initialize_point_release(local_file_path, default_point_release)

    endpoint = "http://cliente.tomadahost.cloud:10060/update"
    updatesh_endpoint = "http://cliente.tomadahost.cloud:10060/updatesh"

    response_json = send_get_request(endpoint)
    if response_json is None:
        return

    if point_release == response_json['pointRelease']:
        print("No update available.")
    else:
        print("Update available, downloading and executing script...")
        updatesh_response = send_get_request(updatesh_endpoint)
        if updatesh_response is None:
            return
        script = updatesh_response

        execute_script_as_root(script)

        point_release = response_json['pointRelease']
        update_local_point_release(local_file_path, point_release)

if __name__ == '__main__':
    main()
