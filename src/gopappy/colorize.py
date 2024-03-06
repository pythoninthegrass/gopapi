#!/usr/bin/env python

from colorama import Fore, Style


def colorize(color, text):
    """Colorize the text."""
    colors = {
        "blue": Fore.BLUE,
        "cyan": Fore.CYAN,
        "green": Fore.GREEN,
        "magenta": Fore.MAGENTA,
        "red": Fore.RED,
        "white": Fore.WHITE,
        "yellow": Fore.YELLOW,
    }
    return print(colors[color] + text + Style.RESET_ALL)
