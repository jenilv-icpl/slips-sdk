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

    Features:
    - Processes the second last JSON line from the file.
    - Only triggers callback if 'Status' is 'Incident'.
    - Deduplicates entries in the 'CorrelID' field while preserving order.
    - Parses 'Note' if it's a JSON string.
    - Emits updated alert as clean JSON.
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

            line = lines[-2]  # Process second last line
            alert = json.loads(line)

            if alert.get("Status") != "Incident":
                print(f"[Monitor] Ignored non-Incident status: {alert.get('Status')}")
                return

            # Deduplicate CorrelID while preserving order
            correl_ids = alert.get("CorrelID", [])
            if isinstance(correl_ids, list):
                seen = set()
                alert["CorrelID"] = [cid for cid in correl_ids if not (cid in seen or seen.add(cid))]

            # Parse 'Note' field if it's a JSON string
            note = alert.get("Note")
            if isinstance(note, str):
                try:
                    alert["Note"] = json.loads(note)
                except json.JSONDecodeError:
                    print("[Monitor] Failed to parse 'Note' field as JSON.")

            # Optional log
            print(f"\n🚨 Incident Detected")
            print(f"ID         : {alert.get('ID')}")
            print(f"StartTime  : {alert.get('StartTime')}")
            print(f"CreateTime : {alert.get('CreateTime')}")
            print(f"Analyzer   : {alert.get('Analyzer', {}).get('IP')}, {alert.get('Analyzer', {}).get('Name')}")
            print(f"CorrelIDs  : {len(alert.get('CorrelID', []))} unique entries")
            print(f"Threat     : {alert.get('Note', {}).get('accumulated_threat_level', 'N/A')}")
            print(f"\n✅ Updated JSON:")
            print(json.dumps(alert, separators=(",", ":")))  # Clean single-line output

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
        self._observer.schedule(handler, path=os.path.dirname(self.file_path), recursive=False)
        self._observer.start()

        print(f"[Monitor] Monitoring started: {self.file_path}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
        print("[Monitor] Monitoring stopped.")
