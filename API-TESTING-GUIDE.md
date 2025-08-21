# Stress Detection API Testing Guide

This comprehensive guide helps you test the Stress Detection API using Postman.

## Prerequisites

1. [Postman](https://www.postman.com/downloads/) installed
2. Backend server running at http://localhost:8000 (or your custom URL)
3. MongoDB running (the API requires a database connection)

## Postman Setup

1. Import the `Stress-Detection-API.postman_collection.json` file into Postman:
   - Open Postman
   - Click "Import" in the upper left
   - Select the collection file or drag and drop it
   - Click "Import" to confirm

2. Create a new environment:
   - Click "Environments" in the sidebar
   - Click "+" to create a new environment
   - Name it "Stress Detection API"
   - Add the following variables:
     - `baseUrl`: `http://localhost:8000` (or your custom URL)
     - `apiKey`: Leave empty for now
     - `deviceId`: Leave empty for now
     - `employeeId`: `EMP_001`
     - `jwtToken`: Leave empty for now
   - Click "Save"
   - Select the environment from the dropdown in the upper right

3. Verify collection settings:
   - Click on the "Stress Detection API" collection
   - Go to the "Variables" tab
   - Make sure the `baseUrl` variable is set correctly
   - Click "Save"

## API Authentication

The API supports two authentication mechanisms:

### 1. Device Authentication (API Key)

Used for device-to-API communication, like the Windows agent submitting stress readings.

Two methods are supported for providing the API key:

1. **HTTP Header**:
   ```
   X-Device-Key: your_api_key
   ```

2. **Query Parameter**:
   ```
   ?api_key=your_api_key
   ```

Example with cURL:
```bash
# Header method
curl -X GET "http://localhost:8000/api/v1/device/device-a1b2c3d4/commands" \
  -H "X-Device-Key: your_api_key"

# Query parameter method
curl -X GET "http://localhost:8000/api/v1/device/device-a1b2c3d4/commands?api_key=your_api_key"
```

### 2. User Authentication (JWT Token)

Used for administrative access to the API, such as viewing employee stress data.

1. **Bearer Token**:
   ```
   Authorization: Bearer your_jwt_token
   ```

Example with cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/employee/stress/history/EMP_001" \
  -H "Authorization: Bearer your_jwt_token"
```

To obtain a JWT token, use the login endpoint with valid credentials.

## Testing Flow

Follow these steps to test the complete API functionality:

### Step 1: Test API Availability

1. Open the "Health Check" request in the "Utilities" folder
2. Send the request without any authentication
3. Verify you receive a 200 OK response with status "ok"

### Step 2: Register a Device

1. Open the "Register Device" request in the "Authentication" folder
2. Verify the request body has:
   ```json
   {
     "employee_id": "{{employeeId}}",
     "device_name": "Test Device",
     "device_type": "windows_agent"
   }
   ```
3. Send the request
4. From the response, copy the `device_id` and `api_key` values
5. Update your Postman environment variables:
   - Set `deviceId` to the received device_id
   - Set `apiKey` to the received api_key
6. Click "Save" to save the environment

### Step 3: Test API Key Authentication

1. Open the "Get Device Commands (Header)" request in the "Device" folder
2. Verify the `X-Device-Key` header is set to `{{apiKey}}`
3. Send the request
4. Verify you receive a 200 OK response (an empty array is normal if no commands exist)

5. Open the "Get Device Commands (Query)" request 
6. Verify the URL includes `?api_key={{apiKey}}`
7. Send the request
8. Verify you receive a 200 OK response

### Step 4: Submit Stress Data

1. Open the "Submit Stress Reading" request in the "Stress" folder
2. Verify the request body has:
   ```json
   {
     "device_id": "{{deviceId}}",
     "employee_id": "{{employeeId}}",
     "stress_level": "High",
     "emotion": "angry",
     "confidence": 0.85,
     "metadata": {
       "face_quality": {
         "brightness": 0.8,
         "clarity": 0.9,
         "face_coverage": 0.85
       }
     }
   }
   ```
   
   Note: `stress_level` must be one of: "Low", "Medium", "High"  
   Note: `emotion` must be one of: "happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"
   
3. Send the request
4. Verify you receive a 201 Created response with a `reading_id`

### Step 5: Test Command Acknowledgment (Optional)

This step requires a command to be present in the system.

1. First, get available commands using the "Get Device Commands" request
2. If a command exists, copy its `command_id`
3. Open the "Acknowledge Command" request
4. Replace the `{commandId}` in the URL with the actual command ID
5. Verify the request body has:
   ```json
   {
     "status": "completed",
     "response": {
       "success": true,
       "message": "Command executed successfully"
     }
   }
   ```
6. Send the request
7. Verify you receive a 200 OK response with the updated command details

### Step 6: Test Administrator Access (Optional)

1. Open the "Login" request in the "Admin" folder
2. Set the request body with valid admin credentials:
   ```json
   {
     "username": "admin@example.com",
     "password": "admin_password"
   }
   ```
3. Send the request
4. Copy the `access_token` from the response
5. Update the `jwtToken` environment variable
6. Open the "Get Employee Stress History" request
7. Verify the `Authorization` header is set to `Bearer {{jwtToken}}`
8. Send the request
9. Verify you receive a 200 OK response with stress history data

## Troubleshooting API Key Issues

If you encounter API key authentication issues:

1. Verify the API key format in Postman matches exactly what was received
2. Try both header-based (`X-Device-Key`) and query parameter (`api_key`) methods
3. Check server logs for any API key validation errors
4. Use the temporary testing bypass by including the device ID in the URL path
5. Re-register the device if needed to obtain a fresh API key

## Error Responses and Status Codes

The API uses standard HTTP status codes to indicate the success or failure of requests:

### Common Status Codes

| Status Code | Meaning | Example Scenario |
|-------------|---------|------------------|
| 200 OK | Request succeeded | Successfully retrieved device commands |
| 201 Created | Resource created | Successfully registered a device |
| 400 Bad Request | Invalid request data | Missing required fields or invalid data format |
| 401 Unauthorized | Authentication failed | Invalid or missing API key |
| 403 Forbidden | Permission denied | Attempting to access another device's data |
| 404 Not Found | Resource not found | Device or endpoint doesn't exist |
| 409 Conflict | Resource conflict | Device ID or employee ID mismatch |
| 500 Internal Server Error | Server error | Database connection failure |

### Error Response Format

Error responses follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Example error (401 Unauthorized):
```json
{
  "detail": "API key is required"
}
```

## Best Practices for API Testing

### 1. Organized Testing Approach

1. **Start with basic connectivity** (Health Check)
2. **Test authentication** before testing authenticated endpoints
3. **Test CRUD operations** in order: Create, Read, Update, Delete
4. **Test error scenarios** by deliberately sending invalid data

### 2. Maintaining Test Data

1. **Use environment variables** for all changeable values
2. **Update variables automatically** using Tests scripts
3. **Reset test data** between test runs when necessary

### 3. Example Postman Test Script

You can add this script to the Tests tab of your "Register Device" request to automatically set environment variables:

```javascript
// Parse response body
var jsonData = pm.response.json();

// Check if device registration was successful
if (pm.response.code === 201 && jsonData.device_id && jsonData.api_key) {
    // Set environment variables
    pm.environment.set("deviceId", jsonData.device_id);
    pm.environment.set("apiKey", jsonData.api_key);
    
    console.log("Environment variables updated with new device credentials");
} else {
    console.error("Failed to update environment variables");
}
```

### 4. Example cURL Commands

Here are examples of testing the API with cURL using the correct data formats:

```bash
# Health check
curl -X GET "http://localhost:8000/api/v1/utils/health"

# Register device
curl -X POST "http://localhost:8000/api/v1/device/register" \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "EMP_001", "device_name": "Test Device"}'

# Get device commands with API key in header
curl -X GET "http://localhost:8000/api/v1/device/device-a1b2c3d4/commands" \
  -H "X-Device-Key: your_api_key"

# Submit stress reading with CORRECT data types
curl -X POST "http://localhost:8000/api/v1/stress/record" \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: your_api_key" \
  -d '{
    "device_id": "device-a1b2c3d4", 
    "employee_id": "EMP_001", 
    "stress_level": "High", 
    "emotion": "angry", 
    "confidence": 85.5, 
    "timestamp": "2025-08-21T12:34:56Z"
  }'
```

## Common API Errors and Solutions

| Error | Possible Cause | Solution |
|-------|----------------|----------|
| "Input should be 'happy', 'neutral'..." | Invalid emotion value | Use only allowed emotion values from the list |
| "Input should be a valid string" | Using a number for stress_level | Change stress_level to "Low", "Medium", or "High" |
| "API key is required" | Missing authentication | Add X-Device-Key header or api_key query parameter |
| "Invalid API key" | Incorrect or expired API key | Re-register the device to get a new API key |
| "Device ID mismatch" | device_id doesn't match authenticated device | Ensure device_id in the body matches your registered device |

## Data Types and Validation

### Stress Level Values
The API expects stress levels to be provided as string values, not numbers. The allowed values are:
- `"Low"` - For low stress levels
- `"Medium"` - For moderate stress levels
- `"High"` - For high stress levels

### Emotion Values
The API accepts the following emotion values:
- `"happy"` - For happy emotions (maps to Low stress)
- `"neutral"` - For neutral emotions (maps to Low stress)
- `"sad"` - For sad emotions (maps to Medium stress)
- `"angry"` - For angry emotions (maps to Medium stress)
- `"fear"` - For fearful emotions (maps to High stress)
- `"disgust"` - For disgusted emotions (maps to High stress)
- `"surprise"` - For surprised emotions (maps to Medium stress)

If you provide an emotion value not in this list (like "stressed" or "worried"), the API will return a validation error.

### Confidence Values
Confidence should be a float value between 0 and 100, representing the confidence percentage of the emotion detection.

## Debugging Common Issues

### Data Validation Issues
- Check required fields in request body
- Ensure data types match (numbers for numeric fields, strings for text)
- Verify format of dates (ISO-8601 format: YYYY-MM-DDThh:mm:ssZ)

### Administrator Access Issues
- Verify JWT token is correctly formatted in the Authorization header
- Check token expiration (tokens typically expire after 24 hours)
- Ensure the user has the correct role/permissions in the database

## API Endpoints Reference

### Health Check
- **URL**: `GET /api/v1/utils/health`
- **Authentication**: None
- **Expected Output**:
  ```json
  {
    "status": "ok",
    "version": "1.0.0",
    "timestamp": "2025-08-21T12:34:56.789Z"
  }
  ```

### Device Registration
- **URL**: `POST /api/v1/device/register`
- **Authentication**: None
- **Request Data**:
  ```json
  {
    "employee_id": "EMP_001",
    "device_name": "John's Laptop",
    "device_type": "windows_agent"  // Optional, defaults to "windows_agent"
  }
  ```
- **Expected Output**:
  ```json
  {
    "device_id": "device-a1b2c3d4",
    "api_key": "f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7",
    "message": "Device registered successfully"
  }
  ```

### Get Device Commands
- **URL**: `GET /api/v1/device/{deviceId}/commands`
- **Authentication**: API Key (header or query parameter)
- **Expected Output**:
  ```json
  [
    {
      "command_id": "cmd-12345678",
      "device_id": "device-a1b2c3d4",
      "command_type": "analyze_now",
      "parameters": {},
      "status": "pending",
      "created_at": "2025-08-21T12:00:00Z",
      "expires_at": "2025-08-21T13:00:00Z"
    }
  ]
  ```

### Submit Stress Reading
- **URL**: `POST /api/v1/stress/record`
- **Authentication**: API Key (header or query parameter)
- **Request Data**:
  ```json
  {
    "device_id": "device-a1b2c3d4",
    "employee_id": "EMP_001",
    "stress_level": "High",
    "emotion": "angry",
    "confidence": 0.85,
    "timestamp": "2025-08-21T12:34:56Z",  // Optional, defaults to current time
    "metadata": {
      "face_quality": {
        "brightness": 0.8,
        "clarity": 0.9,
        "face_coverage": 0.85
      },
      "face_coords": [120, 80, 200, 160]  // Optional
    }
  }
  ```
- **Expected Output**:
  ```json
  {
    "reading_id": "stress-12345678",
    "message": "Stress reading recorded successfully"
  }
  ```

### Acknowledge Command
- **URL**: `POST /api/v1/device/commands/ack/{commandId}`
- **Authentication**: API Key (header or query parameter)
- **Request Data**:
  ```json
  {
    "status": "completed",  // Or "failed"
    "response": {
      "success": true,
      "message": "Command executed successfully",
      "data": {}  // Optional command-specific response data
    }
  }
  ```
- **Expected Output**:
  ```json
  {
    "command_id": "cmd-12345678",
    "device_id": "device-a1b2c3d4",
    "command_type": "analyze_now",
    "status": "completed",
    "created_at": "2025-08-21T12:00:00Z",
    "processed_at": "2025-08-21T12:05:30Z",
    "response": {
      "success": true,
      "message": "Command executed successfully",
      "data": {}
    }
  }
  ```

### Get Employee Stress History
- **URL**: `GET /api/v1/employee/stress/history/{employeeId}`
- **Authentication**: JWT Token (Bearer token)
- **Query Parameters**:
  - `days`: Number of days of history to retrieve (default: 7)
- **Expected Output**:
  ```json
  {
    "employee_id": "EMP_001",
    "employee_name": "John Doe",
    "data_points": 24,
    "period": {
      "start": "2025-08-14T00:00:00Z",
      "end": "2025-08-21T23:59:59Z"
    },
    "readings": [
      {
        "reading_id": "stress-12345678",
        "timestamp": "2025-08-21T12:34:56Z",
        "stress_level": 0.75,
        "emotion": "stressed",
        "device_id": "device-a1b2c3d4"
      }
      // Additional readings...
    ],
    "stress_summary": {
      "average": 0.65,
      "max": 0.88,
      "min": 0.25,
      "trend": "increasing"
    }
  }
  ```

### Admin Login
- **URL**: `POST /api/v1/auth/login`
- **Authentication**: None
- **Request Data**:
  ```json
  {
    "username": "admin@example.com",
    "password": "your_password"
  }
  ```
- **Expected Output**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "usr-12345678",
    "role": "manager"
  }
  ```
