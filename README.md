# PICO_2_WH

A collection of **MicroPython** experiments for the **Raspberry Pi Pico 2 W**.

This repository is a personal workspace for learning and prototyping on the Pico 2 W
microcontroller. Each top-level folder is a small, self-contained project that targets a
single piece of hardware or concept — there is no single application to build or deploy.
The scripts run directly on the board over USB using the
[MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go)
VS Code extension.

## Projects

| Folder | Description |
| --- | --- |
| `board_test_blinks/` | Basic board bring-up tests that flash the onboard LED (`"LED"` pin). |
| `led_blink/` | Blinks an **external** LED wired to GPIO 15. |
| `DHT/` | Reads temperature and humidity from a DHT11 / DHT22 sensor on GPIO 16. |

## Getting started

1. Install [VS Code](https://code.visualstudio.com/) and the **MicroPico** extension.
2. Flash MicroPython onto the Pico 2 W and connect it over USB.
3. Open the folder for the experiment you want to run (e.g. `DHT/`) in VS Code.
4. Use the command palette (`Cmd/Ctrl+Shift+P`) → **MicroPico: Connect**, then
   **MicroPico: Run current file on Pico**.

To stop a running script, press `Ctrl+C` in the Pico REPL or run
**MicroPico: Stop execution**.

To list the files currently on the board, run **MicroPico: List files on Pico**,
or from the Pico REPL:

List Files
```python
import os
os.listdir()      # files in the current directory
os.listdir('/')   # root of the device filesystem
```

Delete files
```python
import os, rp2
os.umount('/')
bdev = rp2.Flash()
os.VfsLfs2.mkfs(bdev)
os.mount(bdev, '/')
```

## Hardware

- **Board:** Raspberry Pi Pico 2 W
- **Onboard LED:** named `"LED"` pin
- **External LED:** GPIO 15
- **DHT11 / DHT22 sensor:** GPIO 16
