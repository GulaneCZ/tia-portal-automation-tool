from pathlib import Path
import argparse
import logging

from src.core import logs

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Internal tooling for Siemens PLC Engineers by Titus Global Tech.")
    parser.add_argument("-j", "--json",
                        type=Path,
                        help="JSON config file path"
                        )
    args = parser.parse_args()

    json_config = args.json

    if not json_config:
        logger.info("Application started as GUI.")
        import sys

        from ui.graphical import MainWindow, app

        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    else:
        logger.info("Application started as TUI.")
        import ui.terminal
