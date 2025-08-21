# API Key Troubleshooting Guide

If you're experiencing API key errors like `401 {"detail":"Invalid API key"}` when using the Windows Agent, follow these steps to resolve the issue:

## Quick Fix

1. Run the API Key Fix Utility by double-clicking `fix_api_key.bat` in the windows_agent folder
2. Follow the on-screen instructions to diagnose and fix your API key issues

## Manual Steps (if the Fix Utility doesn't work)

### 1. Check Agent Status

Run the following command to check your agent's status:

```
python -m windows_agent --status
```

Look for the "API Authentication" status. If it shows "Failed", your API key is invalid.

### 2. Re-register the Device

If your API key is invalid, you'll need to re-register your device:

```
python -m windows_agent --register YOUR_EMPLOYEE_ID --device-name YOUR_DEVICE_NAME
```

Replace:
- `YOUR_EMPLOYEE_ID` with your employee ID
- `YOUR_DEVICE_NAME` with a name for your device (optional)

### 3. Verify Registration

After registering, check the status again:

```
python -m windows_agent --status
```

Both "API Connection" and "API Authentication" should show "OK".

## API Key Storage

The API key is stored in a secure configuration file at `%APPDATA%\StressSense\secure.json`. This file is managed by the Windows Agent and should not be edited manually.

## Contact Support

If you continue to experience issues, contact your system administrator and provide:

1. The complete error message 
2. Output from the `--status` command
3. Any relevant logs from `%USERPROFILE%\StressSense\agent.log`
