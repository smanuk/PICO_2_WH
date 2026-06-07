from machine import lightsleep, deepsleep
import json

import wifi
import weather_sensor

# --- Config ----------------------------------------------------------------
# Settings live in config.json on the device, read at runtime. Edit that file
# (no code change needed) to tune behaviour. Keys:
#   locationName     label for this node, included in the reading output.
#   deep_sleep       False = lightsleep: resumes the loop, keeps the USB REPL
#                          alive (use in dev).
#                    True  = deepsleep: lowest power, but RESETS the board each
#                          cycle (production).
#   interval_seconds delay between reads (DHT22 needs at least 2 seconds).
#   dht_pin          GPIO the sensor's data line is wired to.
DEFAULTS = {
    "locationName": "unknown",
    "deep_sleep": False,
    "interval_seconds": 15,
    "dht_pin": 16,
}


def load_config():
    try:
        with open("config.json") as f:
            cfg = json.load(f)
        # Fill in anything missing from the file with the defaults.
        # (MicroPython has no {**a, **b} dict unpacking, so merge manually.)
        merged = dict(DEFAULTS)
        merged.update(cfg)
        return merged
    except (OSError, ValueError) as e:
        print("Could not read config.json ({}); using defaults.".format(e))
        return dict(DEFAULTS)


def sleep(interval_seconds):
    interval = interval_seconds * 1000
    if interval < 2000:
        interval = 2000

    if config["deep_sleep"]:
        # deepsleep() powers down and RESETS the board, so it never returns --
        # the whole script re-runs from the top on wake.
        deepsleep(interval)
    else:
        # lightsleep() resumes on the next line, keeping the loop (and REPL) alive.
        lightsleep(interval)


config = load_config()

# Bring up WiFi at boot. In deepsleep mode the board resets each cycle, so this
# re-runs (and reconnects) on every wake.
wlan = wifi.connect()

# Initialize the DHT22 sensor
sensor = weather_sensor.create(config["dht_pin"])

# Works for both modes: under deepsleep the board resets so the loop body runs
# once per wake; under lightsleep it iterates normally.
while True:
    sleep(config["interval_seconds"])
    weather_sensor.read_and_report(sensor, config["location"])
