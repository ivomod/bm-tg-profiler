import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger import logger

class BrandMeisterClient:
    BASE_URL = "https://api.brandmeister.network/v2"
    DEFAULT_SLOT = 0

    def __init__(self, device_id, token):
        self.device_id = device_id
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_static_groups(self):
        """Retrieve the list of current static groups for the device."""
        url = f"{self.BASE_URL}/device/{self.device_id}/talkgroup"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve static groups: {response.status_code} - {response.text}")

    def drop_dynamic_groups(self):
        """Drop all dynamic groups for the device."""
        url = f"{self.BASE_URL}/device/{self.device_id}/action/dropDynamicGroups/{self.DEFAULT_SLOT}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            logger.info("Successfully dropped all dynamic groups.")
        else:
            raise Exception(f"Failed to drop dynamic groups: {response.status_code} - {response.text}")

    def drop_current_call(self):
        """Drop the current call for the device."""
        url = f"{self.BASE_URL}/device/{self.device_id}/action/dropCallRoute/{self.DEFAULT_SLOT}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            logger.info("Successfully dropped the current call.")
        else:
            raise Exception(f"Failed to drop the current call: {response.status_code} - {response.text}")

    def reset_connection(self):
        """Reset the BrandMeister connection for the device."""
        url = f"{self.BASE_URL}/device/{self.device_id}/action/removeContext"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            logger.info("Successfully reset connection.")
        else:
            raise Exception(f"Failed to reset connection: {response.status_code} - {response.text}")

    def _delete_single_group(self, group):
        """Delete a single static group."""
        group_id = group['talkgroup']
        group_slot = group['slot']
        url = f"{self.BASE_URL}/device/{self.device_id}/talkgroup/{group_slot}/{group_id}"
        response = requests.delete(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to delete static group {group}: {response.status_code} - {response.text}")
        logger.info(f"Deleted static group {group_id} on slot {group_slot}.")
        return group_id

    def delete_static_groups(self):
        """Delete all existing static groups for the device using multiple threads."""
        static_groups = self.get_static_groups()
        logger.info(f"Deleting {len(static_groups)} static groups.")

        if not static_groups:
            return

        errors = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._delete_single_group, group): group for group in static_groups}
            for future in as_completed(futures):
                group = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error deleting group {group}: {e}")
                    errors.append((group, e))

        logger.info("All threads completed.")
        if errors:
            raise Exception(f"Failed to delete {len(errors)} group(s): {errors}")

    def _add_single_group(self, group):
        """Add a single static group."""
        url = f"{self.BASE_URL}/device/{self.device_id}/talkgroup"
        payload = {"group": group, "slot": self.DEFAULT_SLOT}
        response = requests.post(url, headers={**self.headers, "Content-Type": "application/json"}, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to add static group {group}: {response.status_code} - {response.text}")
        logger.info(f"Added static group {group} to slot {self.DEFAULT_SLOT}.")
        return group

    def set_static_groups(self, static_groups):
        """Set new static groups for the device using multiple threads."""
        if not static_groups:
            return

        errors = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._add_single_group, group): group for group in static_groups}
            for future in as_completed(futures):
                group = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error adding group {group}: {e}")
                    errors.append((group, e))

        logger.info("All threads completed.")
        if errors:
            raise Exception(f"Failed to add {len(errors)} group(s): {errors}")
