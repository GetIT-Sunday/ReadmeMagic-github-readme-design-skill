"""ReadmeMagic - One spell, beautiful README"""

__version__ = "2.0.0"
__author__ = "GetIT-Sunday"
__description__ = "Create professional, beautiful, high-converting README.md files"


def main():
    """Run the command-line interface without importing it at package import time."""
    from .cli import main as cli_main

    return cli_main()


__all__ = ["main", "__version__"]
