import json
import time
from slips.slips_incident_monitor import SlipsIncidentsMonitor  # if saved as slips_incidents_monitor.py

# 1. Define the callback function
def handle_incident(alert: dict):
    print("🚨 Incident Alert Received:")
    print(json.dumps(alert, indent=2))

# 2. Instantiate the monitor
monitor = SlipsIncidentsMonitor("path/to/your/alerts.json", handle_incident)

# 3. Start the monitor
try:
    monitor.start()

    # Keep the main thread alive (simulate daemon)
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[Main] Stopping monitor due to keyboard interrupt.")

# 4. Stop the monitor when done
finally:
    monitor.stop()
