from machine import lightsleep, deepsleep, Pin
import json
import utime

import wifi
import weather_sensor
import reporter
from logger import get_logger

log = get_logger(__name__)


# --- Config ----------------------------------------------------------------
# Settings live in config.json on the device, read at runtime. Edit that file
# (no code change needed) to tune behaviour. Keys:
#   locationName     label for this node, included in the reading output.
#   deep_sleep       False = lightsleep: resumes the loop, keeps the USB REPL
#                          alive (use in dev).
#                    True  = deepsleep: lowest power, but RESETS the board each
#                          cycle (production).
#   dev_sleep        True = plain utime.sleep(5): a busy 5s wait that does NOT
#                          touch the USB connection, so the REPL and print()
#                          output stay alive for debugging. Overrides deep_sleep
#                          and ignores interval_seconds. Leave False otherwise.
#   interval_seconds delay between reads (DHT22 needs at least 2 seconds).
#   dht_pin          GPIO the sensor's data line is wired to.
#   service_url      full URL each reading is POSTed to (host:port + path).
DEFAULTS = {
    "locationName": "unknown",
    "deep_sleep": False,
    "dev_sleep": True,
    "interval_seconds": 15,
    "dht_pin": 16,
    "service_url": "http://octo.homehack.cc:8080/api/readings",
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
        log("Could not read config.json ({}); using defaults.".format(e))
        return dict(DEFAULTS)


def sleep(interval_seconds):
    interval_millis = interval_seconds * 1000
    if interval_millis < 2000:
        interval_millis = 2000

    if config["dev_sleep"]:
        # Plain busy sleep: unlike lightsleep/deepsleep it leaves the CPU clock
        # and USB CDC alone, so the REPL stays connected and print() output keeps
        # flowing. Fixed 5s for debugging; interval_seconds is ignored here.
        utime.sleep(interval_seconds)
    elif config["deep_sleep"]:
        # deepsleep() powers down and RESETS the board, so it never returns --
        # the whole script re-runs from the top on wake.
        deepsleep(interval_millis)
    else:
        # lightsleep() resumes on the next line, keeping the loop alive (but it
        # suspends USB, so the REPL/print() drop during the sleep).
        lightsleep(interval_millis)


config = load_config()
log("Starting temp node: {}".format(config["locationName"]))

led = Pin(15, Pin.OUT)

# Initialize the DHT22 sensor
sensor = weather_sensor.create(config["dht_pin"])
utime.sleep(2) # gives the sensor time to start up.

# Works for both modes: under deepsleep the board resets so the loop body runs
# once per wake; under lightsleep it iterates normally.
while True:

    try:
        led.toggle()

        reading = weather_sensor.read(sensor)
        if reading is not None:

            # Only power up the radio when there's actually something to ship.
            wlan = wifi.connect()
            if wlan is not None:
                reporter.send(config["service_url"], reading, config["locationName"])
            else:
                log("WiFi unavailable; skipping send, reading kept locally: {}".format(reading))
    except Exception as e:
        # Headless, an unhandled exception would just stop the script with no
        # visible traceback. Log it so the next REPL session can see it.
        log("loop error: {}".format(e))
    finally:
        # Leave the LED in a known-off state no matter how the body exited.
        led.off()
        # Power the radio down before sleeping. Leaving WiFi active makes
        # lightsleep() wake immediately, so the loop would never pause.
        wifi.disconnect()

    sleep(config["interval_seconds"])
