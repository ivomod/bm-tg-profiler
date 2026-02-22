import pytest
from unittest.mock import patch, MagicMock, call
from bm_client import BrandMeisterClient


DEVICE_ID = "123456"
TOKEN = "test-token-abc"
BASE_URL = "https://api.brandmeister.network/v2"


@pytest.fixture
def client():
    return BrandMeisterClient(DEVICE_ID, TOKEN, slot=2)


@pytest.fixture
def default_client():
    return BrandMeisterClient(DEVICE_ID, TOKEN)


class TestInit:
    def test_stores_device_id(self, client):
        assert client.device_id == DEVICE_ID

    def test_stores_token(self, client):
        assert client.token == TOKEN

    def test_stores_slot(self, client):
        assert client.slot == 2

    def test_default_slot_is_zero(self, default_client):
        assert default_client.slot == 0

    def test_headers_contain_bearer_token(self, client):
        assert client.headers == {"Authorization": f"Bearer {TOKEN}"}


class TestGetStaticGroups:
    @patch("bm_client.requests.get")
    def test_returns_groups_on_success(self, mock_get, client):
        groups = [{"talkgroup": 260, "slot": 0}]
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=groups))

        result = client.get_static_groups()

        assert result == groups
        mock_get.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/talkgroup",
            headers=client.headers,
        )

    @patch("bm_client.requests.get")
    def test_raises_on_failure(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=403, text="Forbidden")

        with pytest.raises(Exception, match="Failed to retrieve static groups"):
            client.get_static_groups()


class TestDropDynamicGroups:
    @patch("bm_client.requests.get")
    def test_success(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=200)
        client.drop_dynamic_groups()

        mock_get.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/action/dropDynamicGroups/{client.slot}",
            headers=client.headers,
        )

    @patch("bm_client.requests.get")
    def test_raises_on_failure(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=500, text="Server Error")

        with pytest.raises(Exception, match="Failed to drop dynamic groups"):
            client.drop_dynamic_groups()


class TestDropCurrentCall:
    @patch("bm_client.requests.get")
    def test_success(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=200)
        client.drop_current_call()

        mock_get.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/action/dropCallRoute/{client.slot}",
            headers=client.headers,
        )

    @patch("bm_client.requests.get")
    def test_raises_on_failure(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=502, text="Bad Gateway")

        with pytest.raises(Exception, match="Failed to drop the current call"):
            client.drop_current_call()


class TestResetConnection:
    @patch("bm_client.requests.get")
    def test_success(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=200)
        client.reset_connection()

        mock_get.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/action/removeContext",
            headers=client.headers,
        )

    @patch("bm_client.requests.get")
    def test_raises_on_failure(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=401, text="Unauthorized")

        with pytest.raises(Exception, match="Failed to reset connection"):
            client.reset_connection()


class TestDeleteSingleGroup:
    @patch("bm_client.requests.delete")
    def test_deletes_correct_url(self, mock_delete, client):
        mock_delete.return_value = MagicMock(status_code=200)
        group = {"talkgroup": 260, "slot": 1}

        result = client._delete_single_group(group)

        assert result == 260
        mock_delete.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/talkgroup/1/260",
            headers=client.headers,
        )

    @patch("bm_client.requests.delete")
    def test_raises_on_failure(self, mock_delete, client):
        mock_delete.return_value = MagicMock(status_code=404, text="Not Found")
        group = {"talkgroup": 999, "slot": 0}

        with pytest.raises(Exception, match="Failed to delete static group"):
            client._delete_single_group(group)


class TestDeleteStaticGroups:
    @patch("bm_client.requests.delete")
    @patch("bm_client.requests.get")
    def test_deletes_all_groups(self, mock_get, mock_delete, client):
        groups = [
            {"talkgroup": 260, "slot": 0},
            {"talkgroup": 261, "slot": 1},
        ]
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=groups))
        mock_delete.return_value = MagicMock(status_code=200)

        client.delete_static_groups()

        assert mock_delete.call_count == 2

    @patch("bm_client.requests.get")
    def test_noop_when_no_groups(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=[]))
        client.delete_static_groups()

    @patch("bm_client.requests.delete")
    @patch("bm_client.requests.get")
    def test_raises_on_partial_failure(self, mock_get, mock_delete, client):
        groups = [{"talkgroup": 1, "slot": 0}, {"talkgroup": 2, "slot": 0}]
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=groups))

        def side_effect(url, headers=None):
            if "talkgroup/0/1" in url:
                return MagicMock(status_code=200)
            return MagicMock(status_code=500, text="fail")

        mock_delete.side_effect = side_effect

        with pytest.raises(Exception, match="Failed to delete 1 group"):
            client.delete_static_groups()


class TestAddSingleGroup:
    @patch("bm_client.requests.post")
    def test_adds_group(self, mock_post, client):
        mock_post.return_value = MagicMock(status_code=200)

        result = client._add_single_group(26013)

        assert result == 26013
        mock_post.assert_called_once_with(
            f"{BASE_URL}/device/{DEVICE_ID}/talkgroup",
            headers={**client.headers, "Content-Type": "application/json"},
            json={"group": 26013, "slot": client.slot},
        )

    @patch("bm_client.requests.post")
    def test_raises_on_failure(self, mock_post, client):
        mock_post.return_value = MagicMock(status_code=400, text="Bad Request")

        with pytest.raises(Exception, match="Failed to add static group"):
            client._add_single_group(99999)


class TestSetStaticGroups:
    @patch("bm_client.requests.post")
    def test_adds_all_groups(self, mock_post, client):
        mock_post.return_value = MagicMock(status_code=200)

        client.set_static_groups([260, 261, 262])

        assert mock_post.call_count == 3

    def test_noop_when_empty(self, client):
        client.set_static_groups([])

    @patch("bm_client.requests.post")
    def test_raises_on_partial_failure(self, mock_post, client):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return MagicMock(status_code=500, text="fail")
            return MagicMock(status_code=200)

        mock_post.side_effect = side_effect

        with pytest.raises(Exception, match="Failed to add 1 group"):
            client.set_static_groups([1, 2, 3])
