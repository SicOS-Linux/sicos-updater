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
    try:
        with open(local_file_path, 'r') as f:
            data = json.load(f)
            return data['pointRelease'], data['release']
    except FileNotFoundError:
        point_release = default_point_release
        release = 'current_release'  # default value for release
        with open(local_file_path, 'w') as f:
            json.dump({'pointRelease': point_release, 'release': release}, f)
        return point_release, release
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return default_point_release, 'current_release'  # default value for release

def send_get_request(endpoint, json_response=False):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        if json_response:
            return response.json()
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error accessing endpoint: {e}")
        return None

def execute_script_as_root(script):
    try:
        os.system(f"sudo gbs {script}")
    except Exception as e:
        print(f"Error executing script: {e}")

def update_local_point_release(local_file_path, point_release, release):
    with open(local_file_path, 'w') as f:
        json.dump({'pointRelease': point_release, 'release': release}, f)

def main():
    username = get_username()
    local_file_path = get_local_file_path(username)
    default_point_release = get_default_point_release()

    endpoint = "http://cliente.tomadahost.cloud:10060/update"
    updatesh_endpoint = "http://cliente.tomadahost.cloud:10060/updatesh"

    response_json = send_get_request(endpoint, json_response=True)
    if response_json is None:
        return

    local_point_release, local_release = initialize_point_release(local_file_path, default_point_release)

    if local_point_release == response_json['pointRelease'] and local_release == response_json['release']:
        print("No update available.")
    else:
        if local_release != response_json['release']:
            print("Your SicOS version is no longer supported.")
            return
        print("Update available, downloading and executing script...")
        updatesh_response = send_get_request(updatesh_endpoint, json_response=False)
        if updatesh_response is None:
            return
        script = updatesh_response

        execute_script_as_root(script)

        point_release = response_json['pointRelease']
        release = response_json['release']
        update_local_point_release(local_file_path, point_release, release)

if __name__ == '__main__':
    main()
