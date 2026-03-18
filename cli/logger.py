# Copyright (c) 2026 Ivo Modrinić
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re

_EMOJI_RE = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0000FE0F"
    "\U0000200D"
    "\U00002139"
    "\U00002328"
    "\U000023CF"
    "\U000023E9-\U000023F3"
    "\U000023F8-\U000023FA"
    "\U00002934-\U00002935"
    "\U000025AA-\U000025FE"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "]+",
    flags=re.UNICODE,
)


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


class Logger:
    """Simple colorful logger with optional plain mode (no colors/emojis)."""

    def __init__(self, plain=False):
        self.plain = plain

    def _strip_emojis(self, text):
        return _EMOJI_RE.sub("", text).strip()

    def _print(self, message, color, emoji):
        if self.plain:
            print(self._strip_emojis(message))
        else:
            print(f"{color}{Colors.BOLD}{emoji} {message}{Colors.RESET}")

    def info(self, message):
        self._print(message, Colors.CYAN, "ℹ️")

    def error(self, message):
        self._print(message, Colors.RED, "❌")

    def warning(self, message):
        self._print(message, Colors.YELLOW, "⚠️ ")

    def success(self, message):
        self._print(message, Colors.GREEN, "✨")


logger = Logger()
