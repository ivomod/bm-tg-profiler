# Colorful print functions with emoji

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Regular colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


class Logger:
    """Simple colorful logger with emoji"""

    @staticmethod
    def info(message):
        """Print info message in cyan with checkmark emoji"""
        print(f"{Colors.CYAN}{Colors.BOLD}ℹ️ {message}{Colors.RESET}")

    @staticmethod
    def error(message):
        """Print error message in red with cross emoji"""
        print(f"{Colors.RED}{Colors.BOLD}❌ {message}{Colors.RESET}")

    @staticmethod
    def warning(message):
        """Print warning message in yellow with warning emoji"""
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {message}{Colors.RESET}")

    @staticmethod
    def success(message):
        """Print success message in green with sparkles emoji"""
        print(f"{Colors.GREEN}{Colors.BOLD}✨ {message}{Colors.RESET}")


# Create a logger instance
logger = Logger()
