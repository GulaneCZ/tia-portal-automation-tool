import logging
import sys
import warnings

FORMAT: str = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s"

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger = logging.getLogger("UncaughtException")
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def handle_warning(message, category, filename, lineno, file=None, line=None):
    logger = logging.getLogger("Warnings")
    logger.warning(f"{filename}:{lineno}: {category.__name__}: {message}")

class QTextEditHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        try:
            message = self.format(record)
            self.widget.append(message)
        except Exception:
            self.handleError(record)

def setup(level=logging.INFO, textbox=None):
    sys.excepthook = handle_exception
    warnings.showwarning = handle_warning

    logger = logging.getLogger()
    logger.setLevel(level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter(FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if textbox:
        gui_handler = QTextEditHandler(textbox)
        gui_handler.setLevel(level)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
