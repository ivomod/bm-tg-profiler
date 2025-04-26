import requests
import json
import argparse
import sys

BASE_URL = "https://api.brandmeister.network/v2"
DEFAULT_SLOT=0

def load_profile(profile_file):
    """Load static groups from the profile JSON file."""
    try:
        with open(profile_file, 'r') as file:
            return json.load(file).get("static_groups", [])
    except Exception as e:
        print(f"Error loading profile file: {e}")
        sys.exit(1)

def get_static_groups(device_id, token):
    """Retrieve the list of current static groups for the given device."""
    url = f"{BASE_URL}/device/{device_id}/talkgroup"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve static groups: {response.status_code} - {response.text} for {url}")
        sys.exit(1)

def drop_dynamic_groups(device_id, token):
    """Drop all dynamic groups for the given device."""
    url = f"{BASE_URL}/device/{device_id}/action/dropDynamicGroups/{DEFAULT_SLOT}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Successfully dropped all dynamic groups.")
    else:
        print(f"Failed to drop dynamic groups: {response.status_code} - {response.text} for {url}")

def drop_current_call(device_id, token):
    """Drop the current call for the given device."""
    url = f"{BASE_URL}/device/{device_id}/action/dropCallRoute/{DEFAULT_SLOT}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Successfully dropped the current call.")
    else:
        print(f"Failed to drop the current call: {response.status_code} - {response.text} for {url}")


def delete_static_groups(device_id, token):
    """Delete all existing static groups for the given device one by one."""
    static_groups = get_static_groups(device_id, token)
    for group in static_groups:
        group_id = group['talkgroup']
        group_slot = group['slot']
        url = f"{BASE_URL}/device/{device_id}/talkgroup/{group_slot}/{group_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"Successfully deleted static group {group}.")
        else:
            print(f"Failed to delete static group {group}: {response.status_code} - {response.text} for {url}")

def set_static_groups(device_id, token, static_groups):
    """Set new static groups for the given device."""
    url = f"{BASE_URL}/device/{device_id}/talkgroup"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for group in static_groups:
        payload = {"group": group, "slot": DEFAULT_SLOT}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Successfully added static group {group}.")
        else:
            print(f"Failed to add static group {group}: {response.status_code} - {response.text} for {url}")

def main():
    parser = argparse.ArgumentParser(description="Manage static groups for BrandMeister.")
    parser.add_argument("--device_id", required=True, help="The device ID of the repeater.")
    parser.add_argument("--token", required=True, help="The BrandMeister API token.")
    parser.add_argument("--profile_file", required=True, help="Path to the JSON profile file containing static groups.")
    args = parser.parse_args()

    static_groups = load_profile(args.profile_file)
    delete_static_groups(args.device_id, args.token)
    drop_dynamic_groups(args.device_id, args.token)
    drop_current_call(args.device_id, args.token)
    set_static_groups(args.device_id, args.token, static_groups)

if __name__ == "__main__":
    main()