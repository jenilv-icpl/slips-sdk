import os
import time
import json
import threading
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SlipsAlertMonitor:
    """
    Real-time SLIPS alert monitor using watchdog.

    - Watches alert_file_path for new alerts
    - Handles delayed file creation
    - Ignores malformed JSON
    - Production-safe threading and file access
    """

    def __init__(self, alert_file_path: str, on_alert: Callable[[dict], None], start_from_end: bool = True):
        self.alert_file_path = os.path.abspath(alert_file_path)
        self.on_alert = on_alert
        self.start_from_end = start_from_end
        self._running = False
        self._observer: Optional[Observer] = None
        self._file = None
        self._lock = threading.Lock()

    class _AlertFileHandler(FileSystemEventHandler):
        def __init__(self, monitor):
            self.monitor = monitor

        def on_modified(self, event):
            if os.path.abspath(event.src_path) == self.monitor.alert_file_path:
                with self.monitor._lock:
                    self.monitor._read_new_lines()

    def _wait_for_file(self):
        print(f"[Monitor] Waiting for alert file: {self.alert_file_path}")
        wait_start = time.time()
        while not os.path.isfile(self.alert_file_path):
            time.sleep(1)
            if int(time.time() - wait_start) % 10 == 0:
                print(f"[Monitor] Still waiting... ({self.alert_file_path})")
        print(f"[Monitor] Alert file found: {self.alert_file_path}")

    def _read_new_lines(self):
        buffer = self._file.read()
        if not buffer:
            return

        lines = buffer.strip().split('\n')
        for line in lines:
            try:
                alert = json.loads(line)
                self.on_alert(alert)
            except json.JSONDecodeError as e:
                print(f"[Monitor] JSON decode error: {e}. Line skipped.")
            except Exception as ex:
                print(f"[Monitor] Unexpected error: {ex}")

    def start(self):
        self._wait_for_file()

        self._running = True
        self._file = open(self.alert_file_path, "r", buffering=1)

        if self.start_from_end:
            self._file.seek(0, os.SEEK_END)
        else:
            self._read_new_lines()

        event_handler = self._AlertFileHandler(self)
        self._observer = Observer(timeout=0.1)
        directory = os.path.dirname(self.alert_file_path)
        self._observer.schedule(event_handler, path=directory, recursive=False)
        self._observer.start()

        print(f"[Monitor] Monitoring started: {self.alert_file_path}")

    def stop(self):
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
        if self._file:
            self._file.close()
        print("[Monitor] Stopped.")

    def read_all_existing(self):
        self._wait_for_file()
        with open(self.alert_file_path, "r") as f:
            for line in f:
                try:
                    alert = json.loads(line.strip())
                    self.on_alert(alert)
                except json.JSONDecodeError:
                    continue

    def is_running(self) -> bool:
        return self._running
