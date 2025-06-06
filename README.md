# PLC Codesys Mimicking Desktop App Example

A desktop application that simulates a PLC-controlled water tank system, built with Python (PySide6 + pyqtgraph).
This app is designed to mimic Codesys-style logic and HMI for demo, training, or prototyping purposes.

## Features

- **Auto/Manual Mode**: Switch between automatic process simulation and manual control.
- **Realistic Process Simulation**: Tank fills/drains based on pump and valve state.
- **Live Visualization**: Animated tank, pump, valve, and sensor status.
- **Event/Alarm Log**: See all process events and alarms in real time.
- **Live Chart**: Trend tank level and valve opening.
- **Alarms**: High/low level and overfill alarms.
- **User Controls**: Start/stop pump, open/close valve, set tank level (manual mode).

## Demo Video

[Watch the demo video on Loom](https://www.loom.com/share/40add16fdfa045cd9c88898e695db3a0?sid=63ec46b4-d716-4fee-bcaa-685b27a332bc)

## Screenshots

Add a screenshot here if desired (e.g., `screenshot.png`).

## Requirements

- Python 3.8+
- PySide6
- pyqtgraph

## Setup

```bash
git clone https://github.com/Ikarus0013/PLC_CodesysMimicing_DesktopAppExample.git
cd PLC_CodesysMimicing_DesktopAppExample
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python plc_desktop.py
```

## Usage

- **Auto Mode**: The tank fills/drains automatically based on pump/valve logic.
- **Manual Mode**: Use the slider and valve button to set tank level and valve state.
- **Event Log**: See all process events and alarms at the bottom.
- **Switch modes**: Use the radio buttons at the top.

## License

MIT 