# uboot-interupt

A Python tool to reliably interrupt U-Boot on embedded devices via serial port by sending aggressive keypress floods.

## Features

- Multiple spam modes to break into U-Boot prompt
- Configurable duration and intensity
- Cross-platform (Linux, Windows, macOS)

## Requirements

- Python 3.x
- `pyserial` library (`pip install pyserial`)

## Example Commands

```# Continuous spam until success (recommended)
python interupt.py --port /dev/ttyUSB0 --mode continuous

# Timed aggressive spam
python interupt.py --port /dev/ttyUSB0 --mode spam --duration 20

# Nuclear option (maximum flood)
python interupt.py --port /dev/ttyUSB0 --mode nuclear --duration 10```