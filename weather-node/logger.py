# Headless there is no REPL, and lightsleep/deepsleep suspend USB, so print()
# alone leaves no trace of a failure. This module mirrors every message to a
# file on flash so it can be read back later from the REPL:
#     print(open("node.log").read())
#
# Named logger.py, not logging.py, to avoid colliding with the micropython-lib
# `logging` module some setups ship.
import os
import utime

LOG_PATH = "node.log"
# Two-file rotation: when LOG_PATH passes MAX_BYTES it is rolled to OLD_PATH
# (replacing the previous generation) and a fresh LOG_PATH is started. Worst
# case on disk is ~2 * MAX_BYTES, so the log can never run flash out of space.
OLD_PATH = LOG_PATH + ".1"
MAX_BYTES = 32 * 1024


def _file_size(path):
    try:
        return os.stat(path)[6]  # st_size
    except OSError:
        return 0  # not there yet


def _rotate():
    # os.rename won't overwrite an existing target on littlefs, so drop the
    # old generation first. Each step is guarded -- rotation must never raise.
    try:
        os.remove(OLD_PATH)
    except OSError:
        pass
    try:
        os.rename(LOG_PATH, OLD_PATH)
    except OSError:
        pass


def log(msg, name=None):
    if name:
        line = "{}: [{}] {}".format(utime.time(), name, msg)
    else:
        line = "{}: {}".format(utime.time(), msg)
    print(line)
    try:
        if _file_size(LOG_PATH) > MAX_BYTES:
            _rotate()
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError:
        # Never let logging itself take down the loop.
        pass


def get_logger(name):
    """Return a log() bound to a source name, so each line shows where it came
    from. Usage in a module:  log = get_logger(__name__)"""
    def _log(msg):
        log(msg, name)
    return _log
