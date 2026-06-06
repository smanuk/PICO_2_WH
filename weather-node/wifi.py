import network
import time
import json


def connect(timeout_s=20, secrets_path="secrets.json"):
    # Credentials live in secrets.json (gitignored). Missing/bad file is not
    # fatal -- we return None so the caller can still run the sensor locally.
    try:
        with open(secrets_path) as f:
            secrets = json.load(f)
    except (OSError, ValueError) as e:
        print("No usable {} ({}); skipping WiFi.".format(secrets_path, e))
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi '{}'...".format(secrets["ssid"]))
        wlan.connect(secrets["ssid"], secrets["password"])
        # ticks_diff handles the counter wrapping; plain subtraction wouldn't.
        deadline = time.ticks_add(time.ticks_ms(), timeout_s * 1000)
        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                print("WiFi connection timed out.")
                return None
            time.sleep_ms(250)
    print("WiFi connected. IP: {}".format(wlan.ifconfig()[0]))
    return wlan
