import machine
import time

from machine import Pin

LED_NAME = "LED"
led = Pin(LED_NAME, Pin.OUT)

while True:
    led.value(1)  # Turn on the LED
    time.sleep(1)  # Wait for 1 second
    led.value(0)  # Turn off the LED
    time.sleep(1)  # Wait for 1 second