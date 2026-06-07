# Ships a reading to the collection service over HTTP. Kept as its own module
# (like wifi.py / weather_sensor.py) so main.py stays orchestration-only.
try:
    import urequests as requests
except ImportError:
    # Newer micropython-lib ships this as `requests`.
    import requests
import json


def send(url, reading, location_name):
    """POST a reading (plus its location name) to the service.

    Returns True on a 2xx response. Network/HTTP failure is non-fatal: it is
    logged and False returned so the sensor loop keeps running locally.
    """
    payload = {
        "locationName": location_name,
        "temperature": reading["temperature"],
        "humidity": reading["humidity"],
    }
    resp = None
    try:
        # Serialise ourselves + set the header explicitly so we don't depend on
        # a particular urequests version doing it for us.
        resp = requests.post(
            url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        ok = 200 <= resp.status_code < 300
        if not ok:
            print("Service returned HTTP {}.".format(resp.status_code))
        return ok
    except OSError as e:
        print("Failed to send reading to {} ({}).".format(url, e))
        return False
    finally:
        # Always close, or MicroPython leaks the socket and later POSTs fail.
        if resp is not None:
            resp.close()