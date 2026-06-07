# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A collection of **MicroPython** scripts for the **Raspberry Pi Pico 2 W**. Each top-level
folder (`DHT/`, `board_test_blinks/`, `led_blink/`, `weather-node/`) is an independent,
self-contained experiment, not a module of a larger application. There is no build system,
package manifest, or test suite — these are standalone scripts flashed to and run directly
on the microcontroller.

Most folders are single throwaway scripts; **`weather-node/` is the exception** — it is a
small multi-file application (see its own section below) and is the direction the project is
heading.

## Running code on the Pico

Development is done in VS Code with the **MicroPico** extension (`paulober.pico-w-go`,
listed in `.vscode/extensions.json`). The board connects over USB serial; only one program
(VS Code, Thonny, a serial monitor) can hold the port at a time.

Use the command palette (`Cmd+Shift+P`):
- **`MicroPico: Connect`** — attach to the board (status shows "Pico Connected" in the status bar)
- **`MicroPico: Run current file on Pico`** — run the open script
- **`MicroPico: Stop execution`**, or **`Ctrl+C`** in the Pico REPL — halt a running script
- **`MicroPico: Delete file from board`** — remove a file from the device

A file named `main.py` on the device **auto-runs on every power-up/reset**. To stop that
permanently, halt with `Ctrl+C`, then delete/rename it (`import os; os.remove('main.py')`
in the REPL). The throwaway scripts use plain filenames (`blink1.py`, `dht11.py`), so they
only run when explicitly invoked. **`weather-node/main.py` intentionally uses that name** so
the node boots and starts logging on power-up — convenient for deployment, but it means it
also runs on every reset during development.

## Project layout note

Each folder carries its own `.micropico` marker and `.vscode/` config. The `.micropico`
file is what activates the MicroPico extension — so **open the specific subfolder** (e.g.
`DHT/`) as the VS Code workspace, not just an individual file, for the extension's controls
to appear. Editor/tab filename colors are Git status (orange = modified tracked file,
green = untracked/new), unrelated to file type.

## Hardware conventions used by the scripts

- **Onboard LED**: `Pin("LED", Pin.OUT)` — the named "LED" pin (Pico W has no fixed GPIO for it)
- **External LED**: GPIO **15** (`led_blink/external_led_blink.py`)
- **DHT temperature/humidity sensor**: data on GPIO **16**, read via the built-in `dht`
  module (`DHT11` in `dht11.py`, `DHT22` in `dht22.py`); poll loop sleeps 2s and catches
  `OSError` on failed reads

Loops that drive hardware should leave outputs in a safe state on exit — prefer wrapping
the `while True:` in `try/finally` (or catching `KeyboardInterrupt`) and turning the LED
off, as in `external_led_blink.py` and `blink2.py`.

## The `weather-node/` app (multi-file)

Unlike the single-script folders, `weather-node/` is split into modules that all live on
the device and import each other at runtime:

- **`main.py`** — orchestration: loads config, brings up WiFi, inits the sensor, runs the
  poll/sleep loop. Auto-runs on boot (see above).
- **`wifi.py`** — `wifi.connect()` reads credentials and connects the station interface with
  a timeout; returns the `wlan` object or `None`. A missing/failed connection is non-fatal so
  the sensor loop still runs locally.
- **`weather_sensor.py`** — `create(pin)` inits the DHT22; `read_and_report(sensor, location)`
  measures and prints. **Deliberately not named `dht.py`** — that would shadow the built-in
  `dht` module it imports.

Conventions specific to this app:

- **Runtime config is data, not code.** `config.json` holds tunables (`location`,
  `deep_sleep`, `interval_seconds`, `dht_pin`) read at startup via `load_config()`, which
  merges over `DEFAULTS` so a missing file/key falls back gracefully.
- **Secrets are gitignored.** WiFi credentials live in `secrets.json` (ignored by the root
  `.gitignore`); `secrets.example.json` is the committed template. Never commit real
  credentials.
- **Sleep mode toggle:** `deep_sleep` switches between `lightsleep` (resumes the loop, keeps
  the REPL alive — dev) and `deepsleep` (lowest power, but resets the board each cycle —
  production). The single `while True:` loop works for both because deepsleep re-runs the
  whole script from the top on wake.
- **Uploading:** all modules **and** `config.json` / `secrets.json` must be present on the
  device, or `import` fails at boot. Use *Upload project to Pico*, not single-file upload.

## Editor / type-checking setup

`.vscode/settings.json` points Pylance at the MicroPython stubs in `~/.micropico-stubs/included`
(via `python.analysis.extraPaths` / `typeshedPaths`) so that `machine`, `utime`, `dht`, etc.
resolve. `reportMissingModuleSource` is silenced because those modules only exist on-device.
Type checking is `basic`.

## Git workflow

History follows a per-experiment feature-branch pattern, each merged into `develop`
(e.g. `external_led_blink` → `develop`). The default branch for PRs is `main`.

## C SDK note

`pico_sdk_import.cmake` files are present but currently unused — there are no `CMakeLists.txt`
or C sources. They are scaffolding for a potential Pico C/C++ SDK build and can be ignored
for the MicroPython work.
