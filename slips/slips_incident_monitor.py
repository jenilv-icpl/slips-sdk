import os
import time
import json
import threading
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SlipsIncidentsMonitor:
    """
    Monitors a file containing multiple JSON alert lines.

    - Processes the second last line only (useful for handling delays in file writes).
    - Calls the callback only if "Status" is "Incident".
    - Deduplicates entries in the 'CorrelID' field.
    """

    def __init__(self, file_path: str, on_incident_alert: Callable[[dict], None]):
        self.file_path = os.path.abspath(file_path)
        self.on_incident_alert = on_incident_alert
        self._observer: Optional[Observer] = None
        self._lock = threading.Lock()

    class _FileModifiedHandler(FileSystemEventHandler):
        def __init__(self, monitor: 'SlipsIncidentsMonitor'):
            self.monitor = monitor

        def on_modified(self, event):
            if os.path.abspath(event.src_path) == self.monitor.file_path:
                with self.monitor._lock:
                    self.monitor._process_second_last_line()

    def _wait_for_file(self):
        print(f"[Monitor] Waiting for alert file: {self.file_path}")
        while not os.path.isfile(self.file_path):
            time.sleep(0.5)
        print(f"[Monitor] Alert file detected: {self.file_path}")

    def _process_second_last_line(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) < 2:
                print("[Monitor] Not enough lines to process second last.")
                return

            target_line = lines[-2]  # Second last line

            alert = json.loads(target_line)

            if alert.get("Status") != "Incident":
                print("[Monitor] Ignoring non-Incident alert.")
                return

            if isinstance(alert.get("CorrelID"), list):
                seen = set()
                alert["CorrelID"] = [cid for cid in alert["CorrelID"] if not (cid in seen or seen.add(cid))]

            self.on_incident_alert(alert)

        except json.JSONDecodeError as e:
            print(f"[Monitor] JSON decode error: {e}")
        except Exception as e:
            print(f"[Monitor] Unexpected error: {e}")

    def start(self):
        self._wait_for_file()
        self._process_second_last_line()

        handler = self._FileModifiedHandler(self)
        self._observer = Observer(timeout=0.2)
        self._observer.schedule(handler, os.path.dirname(self.file_path), recursive=False)
        self._observer.start()

        print(f"[Monitor] Monitoring started: {self.file_path}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
        print("[Monitor] Monitoring stopped.")
