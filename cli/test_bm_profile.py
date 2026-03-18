# Copyright (c) 2026 Ivo Modrinić
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from bm_profile import load_profile, main


class TestLoadProfile:
    def test_loads_static_groups(self, tmp_path):
        profile = {"static_groups": [260, 261, 262]}
        profile_file = tmp_path / "test.json"
        profile_file.write_text(json.dumps(profile))

        result = load_profile(str(profile_file))

        assert result == [260, 261, 262]

    def test_returns_empty_list_when_key_missing(self, tmp_path):
        profile_file = tmp_path / "empty.json"
        profile_file.write_text("{}")

        result = load_profile(str(profile_file))

        assert result == []

    def test_exits_on_missing_file(self):
        with pytest.raises(SystemExit):
            load_profile("/nonexistent/path/to/profile.json")

    def test_exits_on_invalid_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json at all")

        with pytest.raises(SystemExit):
            load_profile(str(bad_file))


class TestMain:
    @patch("bm_profile.BrandMeisterClient")
    @patch("bm_profile.load_profile", return_value=[260, 261])
    def test_happy_path(self, mock_load, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        args = [
            "bm_profile.py",
            "--device_id", "123",
            "--token", "tok",
            "--profile_file", "p.json",
            "--slot", "2",
        ]
        with patch("sys.argv", args):
            main()

        mock_load.assert_called_once_with("p.json")
        mock_client_cls.assert_called_once_with("123", "tok", slot=2)
        mock_client.delete_static_groups.assert_called_once()
        mock_client.drop_dynamic_groups.assert_called_once()
        mock_client.drop_current_call.assert_called_once()
        mock_client.reset_connection.assert_called_once()
        mock_client.set_static_groups.assert_called_once_with([260, 261])

    @patch("bm_profile.BrandMeisterClient")
    @patch("bm_profile.load_profile", return_value=[260])
    def test_default_slot(self, mock_load, mock_client_cls):
        mock_client_cls.return_value = MagicMock()

        args = [
            "bm_profile.py",
            "--device_id", "123",
            "--token", "tok",
            "--profile_file", "p.json",
        ]
        with patch("sys.argv", args):
            main()

        mock_client_cls.assert_called_once_with("123", "tok", slot=0)

    @patch("bm_profile.BrandMeisterClient")
    @patch("bm_profile.load_profile", return_value=[260])
    def test_exits_on_client_error(self, mock_load, mock_client_cls):
        mock_client = MagicMock()
        mock_client.delete_static_groups.side_effect = Exception("API down")
        mock_client_cls.return_value = mock_client

        args = [
            "bm_profile.py",
            "--device_id", "123",
            "--token", "tok",
            "--profile_file", "p.json",
        ]
        with patch("sys.argv", args):
            with pytest.raises(SystemExit):
                main()

    @patch("bm_profile.BrandMeisterClient")
    @patch("bm_profile.load_profile", return_value=[260])
    def test_plain_print_flag(self, mock_load, mock_client_cls):
        mock_client_cls.return_value = MagicMock()

        args = [
            "bm_profile.py",
            "--device_id", "123",
            "--token", "tok",
            "--profile_file", "p.json",
            "--plain-print",
        ]
        with patch("sys.argv", args):
            with patch("bm_profile.logger") as mock_logger:
                main()
                assert mock_logger.plain is True

    @patch("bm_profile.BrandMeisterClient")
    @patch("bm_profile.load_profile", return_value=[260])
    def test_operations_called_in_order(self, mock_load, mock_client_cls):
        """Verify the API calls happen in the expected sequence."""
        call_order = []
        mock_client = MagicMock()

        mock_client.delete_static_groups.side_effect = lambda: call_order.append("delete")
        mock_client.drop_dynamic_groups.side_effect = lambda: call_order.append("drop_dyn")
        mock_client.drop_current_call.side_effect = lambda: call_order.append("drop_call")
        mock_client.reset_connection.side_effect = lambda: call_order.append("reset")
        mock_client.set_static_groups.side_effect = lambda g: call_order.append("set")
        mock_client_cls.return_value = mock_client

        args = [
            "bm_profile.py",
            "--device_id", "123",
            "--token", "tok",
            "--profile_file", "p.json",
        ]
        with patch("sys.argv", args):
            main()

        assert call_order == ["delete", "drop_dyn", "drop_call", "reset", "set"]
