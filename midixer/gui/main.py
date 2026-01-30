"""Main entry point for midixer GUI"""

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .window import MidixerWindow


def main():
    """Main entry point for GUI"""
    window = MidixerWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
