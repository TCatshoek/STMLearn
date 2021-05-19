from pathlib import Path
import time
import threading
from enum import Enum, unique, auto
import atexit


@unique
class Log(Enum):
    MEMBERSHIP = auto()
    EQUIVALENCE = auto()
    TEST = auto()
    STATE_COUNT = auto()
    ERR_COUNT = auto()
    ERRORS = auto()


# Alex Martelli's 'Borg'
class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


def _log_writer():
    logger = Logger()
    time_waited = 0

    while not logger._quitting:

        if time_waited >= logger.log_interval:
            logger.write()
            time_waited = 0

        time.sleep(1)
        time_waited += 1

    # Write one last time
    logger.write()


class Logger(Borg):
    did_init = False

    def __init__(self):
        Borg.__init__(self)

        if not Logger.did_init:
            self.log_path = None
            self.log_file = None
            self.write_on_change = set()
            self.log_interval = 60
            self.data = {}
            self._lock = threading.Lock()
            self._write_thread = threading.Thread(
                target=_log_writer,
                daemon=True
            )
            self._write_thread_started = False
            self._quitting = False

        Logger.did_init = True

        if not self._write_thread_started:
            self._write_thread_started = True
            self._write_thread.start()

    def _get_time(self):
        return time.time()

    def reset(self):
        self.data = {}

    def set_log_path(self, log_path):
        self.log_path = log_path

        if Path(self.log_path).exists():
            raise Exception("Log file exists")

        self.log_file = open(self.log_path, 'w')
        self.write()

    def set_log_interval(self, log_interval):
        self.log_interval = log_interval

    def set_write_on_change(self, properties):
        self.write_on_change = properties

    def write(self):
        if self.log_file is None:
            return

        with self._lock:
            logtime = self._get_time()
            print("Writing", logtime)
            self.log_file.write(f'{logtime}, ')
            values = [f'{k}:{v}' for k, v in self.data.items()]
            self.log_file.write(", ".join(values))
            self.log_file.write('\n')
            self.log_file.flush()

    def increment(self, key):
        if key not in self.data:
            self.data[key] = 1
        else:
            self.data[key] = self.data[key] + 1

        if self.write_on_change is not None and key in self.write_on_change:
            self.write()

    def add(self, key, value):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(value)

        if self.write_on_change is not None and key in self.write_on_change:
            self.write()

    def set(self, key, value):
        did_change = False
        if key not in self.data:
            self.data[key] = value
            did_change = True
        else:
            old_value = self.data[key]
            self.data[key] = value
            if old_value != value:
                did_change = True

        if did_change and self.write_on_change is not None and key.name in self.write_on_change:
            self.write()


# Parses a log file into a pandas df compatible dict
def parse_log(path):
    with open(path, 'r') as file:
        lines_read = 0
        data = {'timestamp': []}
        starttime = None
        for line in file.readlines():
            # Parse line
            line_data = list(filter(lambda x: len(x) > 0, [x.strip() for x in line.split(',')]))
            time, records = float(line_data[0]), line_data[1:]

            # Time logging
            if starttime is None:
                starttime = time
            data['timestamp'].append(time - starttime)

            # Rest of the data
            for record in records:
                name, value = record.split(':')
                if name not in data:
                    data[name] = [0] * lines_read
                data[name].append(value)

            lines_read += 1

        return data


# Add a shutdown hook to write the logs one last time on exit
def _on_quit():
    logger = Logger()
    logger.write()
    print("Clean shutdown")


atexit.register(_on_quit)
