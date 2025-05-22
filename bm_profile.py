from bm_client import BrandMeisterClient
import argparse
import json
import sys

def load_profile(profile_file):
    """Load static groups from the profile JSON file."""
    try:
        with open(profile_file, 'r') as file:
            return json.load(file).get("static_groups", [])
    except Exception as e:
        print(f"Error loading profile file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Manage static groups for BrandMeister.")
    parser.add_argument("--device_id", required=True, help="The device ID of the repeater.")
    parser.add_argument("--token", required=True, help="The BrandMeister API token.")
    parser.add_argument("--profile_file", required=True, help="Path to the JSON profile file containing static groups.")
    args = parser.parse_args()

    static_groups = load_profile(args.profile_file)
    client = BrandMeisterClient(args.device_id, args.token)

    try:
        client.delete_static_groups()
        client.drop_dynamic_groups()
        client.drop_current_call()
        client.reset_connection()
        client.set_static_groups(static_groups)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()