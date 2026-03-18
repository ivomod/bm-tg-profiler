# Copyright (c) 2026 Ivo Modrinić
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import pytest
from unittest.mock import patch
from logger import Logger, Colors, _EMOJI_RE


class TestEmojiRegex:
    def test_strips_common_emojis(self):
        assert _EMOJI_RE.sub("", "🗑️ Deleted group") == " Deleted group"

    def test_strips_multiple_emojis(self):
        assert _EMOJI_RE.sub("", "🎉✨ Done!") == " Done!"

    def test_leaves_plain_text_untouched(self):
        assert _EMOJI_RE.sub("", "no emojis here") == "no emojis here"

    def test_strips_info_emoji(self):
        result = _EMOJI_RE.sub("", "ℹ️ info message")
        assert "info message" in result


class TestLoggerPlainMode:
    def test_plain_false_by_default(self):
        log = Logger()
        assert log.plain is False

    def test_plain_can_be_enabled(self):
        log = Logger(plain=True)
        assert log.plain is True

    def test_strip_emojis_removes_emojis(self):
        log = Logger()
        assert log._strip_emojis("🗑️ Deleted group 123") == "Deleted group 123"

    def test_strip_emojis_preserves_plain_text(self):
        log = Logger()
        assert log._strip_emojis("plain text") == "plain text"


class TestLoggerOutput:
    @patch("builtins.print")
    def test_info_plain(self, mock_print):
        log = Logger(plain=True)
        log.info("test message")
        mock_print.assert_called_once_with("test message")

    @patch("builtins.print")
    def test_error_plain(self, mock_print):
        log = Logger(plain=True)
        log.error("something failed")
        mock_print.assert_called_once_with("something failed")

    @patch("builtins.print")
    def test_warning_plain(self, mock_print):
        log = Logger(plain=True)
        log.warning("careful now")
        mock_print.assert_called_once_with("careful now")

    @patch("builtins.print")
    def test_success_plain(self, mock_print):
        log = Logger(plain=True)
        log.success("all good")
        mock_print.assert_called_once_with("all good")

    @patch("builtins.print")
    def test_info_colored(self, mock_print):
        log = Logger(plain=False)
        log.info("hello")
        output = mock_print.call_args[0][0]
        assert Colors.CYAN in output
        assert Colors.BOLD in output
        assert "hello" in output
        assert Colors.RESET in output

    @patch("builtins.print")
    def test_error_colored(self, mock_print):
        log = Logger(plain=False)
        log.error("boom")
        output = mock_print.call_args[0][0]
        assert Colors.RED in output
        assert "boom" in output

    @patch("builtins.print")
    def test_success_colored(self, mock_print):
        log = Logger(plain=False)
        log.success("done")
        output = mock_print.call_args[0][0]
        assert Colors.GREEN in output
        assert "done" in output

    @patch("builtins.print")
    def test_warning_colored(self, mock_print):
        log = Logger(plain=False)
        log.warning("hmm")
        output = mock_print.call_args[0][0]
        assert Colors.YELLOW in output
        assert "hmm" in output

    @patch("builtins.print")
    def test_plain_strips_emojis_from_message(self, mock_print):
        log = Logger(plain=True)
        log.info("🗑️ Deleted group 42")
        mock_print.assert_called_once_with("Deleted group 42")
