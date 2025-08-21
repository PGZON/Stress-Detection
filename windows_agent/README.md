# StressSense Windows Agent

A background application for stress detection and monitoring.

## Overview

StressSense Windows Agent is a background application that runs on Windows devices, periodically captures images from the webcam, analyzes them for stress levels using facial emotion detection, and submits the data to a central StressSense backend API.

## Features

- Silent background operation
- Secure local storage of credentials with Windows DPAPI
- Configurable detection intervals
- Command-based control from backend API
- Automatic device registration
- Can be run as a Windows service

## Requirements

- Windows 10 or later
- Webcam
- Python 3.8 or later
- Required Python packages (see `requirements.txt`)
- StressSense backend API

## Installation

### From Source

1. Clone the repository:
```
git clone https://github.com/yourusername/stress-detection.git
cd stress-detection/windows_agent
```

2. Install the required Python packages:
```
pip install -r requirements.txt
```

3. Configure the agent:
```
python -m windows_agent --configure
```

4. Register the device with an employee ID:
```
python -m windows_agent --register EMPLOYEE_ID
```

### Using Executable

1. Download the latest release executable from [Releases](https://github.com/yourusername/stress-detection/releases)

2. Run the executable with configuration parameters:
```
StressSenseAgent.exe --configure
StressSenseAgent.exe --register EMPLOYEE_ID
```

## Running the Agent

### As a Command-line Application

```
StressSenseAgent.exe --run
```

or simply:

```
StressSenseAgent.exe
```

### As a Windows Service

Install the service:
```
StressSenseAgent.exe --startup auto install
```

Start the service:
```
StressSenseAgent.exe start
```

Stop the service:
```
StressSenseAgent.exe stop
```

Remove the service:
```
StressSenseAgent.exe remove
```

## Command-line Options

- `--run`: Run the agent (default if no other options provided)
- `--register EMPLOYEE_ID`: Register this device with the given employee ID
- `--device-name NAME`: Specify device name for registration
- `--configure`: Configure the agent interactively
- `--api-url URL`: Set the API URL
- `--test-connection`: Test connection to the API
- `--status`: Show agent status

## Building the Executable

To build a standalone executable:

```
python build.py
```

The executable will be created in the `dist` folder.

## Security

- Device credentials are stored securely using Windows Data Protection API (DPAPI)
- API communications use API key authentication
- No images are stored locally by default

## Troubleshooting

Logs are stored in `~/StressSense/agent.log` and can help diagnose issues.

Common issues:
- Webcam access issues - ensure your webcam is working and not in use by another application
- API connection issues - check your API URL and ensure the backend is running
- Registration issues - ensure your employee ID is valid

## License

This project is licensed under the MIT License - see the LICENSE file for details.
