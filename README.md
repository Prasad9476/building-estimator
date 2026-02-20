# Building Estimation System - Server Setup Guide

## Quick Start

### Option 1: Using the Startup Script (Recommended)
1. Double-click `run_server.bat` in the project folder
2. The script will:
   - Detect your computer's IP address
   - Start the server
   - Show you the local and network URLs

### Option 2: Manual Start
1. Open Command Prompt in the project folder
2. Run: `python app.py`
3. Find your IP address by running `ipconfig` in another Command Prompt

## Accessing the Server

Once the server is running:

### From the Same Computer:
- Open browser: `http://localhost:5000`

### From Other Computers on the Same Network:
1. Find the host computer's IP address (shown when running `run_server.bat` or via `ipconfig`)
2. On other computers, open: `http://<IP-ADDRESS>:5000`
   - Example: `http://192.168.1.100:5000`

## Requirements

- Python 3.7 or higher
- Flask installed (`pip install flask`)

## Installation

If Flask is not installed, run:
```
pip install flask
```

## File Structure

```
kaushik mini/
├── app.py                 # Main Flask application
├── calculations.py        # Material calculation logic
├── templates/
│   ├── index.html        # Input form
│   ├── result.html       # Results page
│   └── error.html        # Error page
├── run_server.bat        # Startup script
└── README.md             # This file
```

## Features

✅ Advanced building estimation with detailed inputs:
- Plot dimensions (sq.ft)
- Floor specifications
- Foundation details
- RCC structure (columns, beams, slabs)
- Wall details
- Finishing materials

✅ Accurate material calculations:
- Cement quantities (by purpose)
- Sand requirements
- Aggregate quantities
- Steel reinforcement (by component)
- Brickwork materials
- Finishing materials & costs

✅ Multi-user access via network

✅ Cross-platform HTTP access

## Tips for Network Access

1. **Find your IP address:**
   - Run `run_server.bat` (IP is shown)
   - Or run `ipconfig` in Command Prompt and look for "IPv4 Address"

2. **Firewall Rules:**
   - If others can't connect, check Windows Firewall settings
   - Allow Python through the firewall, or
   - Disable firewall temporarily for testing

3. **Network Requirements:**
   - All devices must be on the same WiFi/network
   - Or manually configure routing for different networks

## Output

The system generates detailed estimates including:
- Concrete volumes (PCC, RCC by component)
- Cement requirements in bags
- Sand in cubic meters
- Aggregate quantities
- Steel reinforcement in kg
- Brick count and mortar volume
- Finishing materials (tiles, paint, plaster)
- Total cost estimation in INR (₹)

## Troubleshooting

**Can't connect from other computers:**
1. Verify both computers are on same network
2. Check Windows Firewall is allowing connections
3. Verify IP address is correct
4. Try pinging the host computer

**Port already in use:**
- Edit `app.py` and change port 5000 to another port (e.g., 5001)

**Python not found:**
- Ensure Python is installed and added to PATH
- Run from Command Prompt in the project directory

---

For more help or issues, check that all files are in the correct directory structure.
