from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Body, Query
from typing import List, Any, Dict
from app.schemas.schemas import Command, CommandUpdate
from app.models.models import get_pending_commands, update_command
from app.core.security.deps import verify_device_api_key, limiter
import logging
from datetime import datetime
import uuid
import hashlib
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{device_id}/commands", response_model=List[Command])
@limiter.limit("30/minute")
async def get_device_commands(
    request: Request,
    device_id: str,
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Any:
    """
    Get pending commands for a device.
    API key can be provided either in X-Device-Key header or as api_key query parameter.
    """
    try:
        # Ensure the device ID in the URL matches the one associated with the API key
        if device_id != device.get("device_id") and not device.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Device ID mismatch"
            )
        
        # Get pending commands for the device
        commands = get_pending_commands(device_id)
        
        # Clean MongoDB _id from results
        for cmd in commands:
            if "_id" in cmd:
                cmd.pop("_id")
        
        return commands
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving device commands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred retrieving commands"
        )

@router.post("/commands/ack/{command_id}", response_model=Command)
async def acknowledge_command(
    command_id: str,
    update_data: CommandUpdate,
    request: Request,
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Any:
    """
    Acknowledge or complete a command.
    API key can be provided either in X-Device-Key header or as api_key query parameter.
    """
    try:
        # Update command status
        update_command(command_id, update_data)
        
        # Get updated command
        from app.db.mongodb import commands_collection
        command = commands_collection.find_one({"command_id": command_id})
        
        if not command:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Command not found"
            )
        
        # Clean MongoDB _id
        if "_id" in command:
            command.pop("_id")
        
        return command
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred updating command"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_device(
    request: Request,
    data: Dict[str, Any] = Body(...)
) -> Any:
    """
    Register a new device
    """
    try:
        employee_id = data.get("employee_id")
        device_name = data.get("device_name")
        device_type = data.get("device_type", "windows_agent")
        
        if not employee_id or not device_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields"
            )
        
        # Generate a unique device ID
        device_id = f"device-{uuid.uuid4().hex[:8]}"
        
        # Generate an API key - we'll use a simple hash for consistency
        api_key_raw = f"{device_id}:{uuid.uuid4().hex}:{datetime.utcnow().isoformat()}"
        api_key = hashlib.sha256(api_key_raw.encode()).hexdigest()
        
        # Import hash_api_key to properly hash the key for storage
        from app.core.security.auth import hash_api_key
        api_key_hash = hash_api_key(api_key)
        
        # Get existing device for this employee if any
        from app.db.mongodb import devices_collection
        existing_device = devices_collection.find_one({"employee_id": employee_id, "device_type": device_type})
        
        if existing_device:
            # Update existing device instead of creating a new one
            logger.info(f"Updating existing device for employee {employee_id}")
            
            # Update device with new keys and info
            devices_collection.update_one(
                {"_id": existing_device["_id"]},
                {"$set": {
                    "device_name": device_name,
                    "api_key": api_key,
                    "api_key_hash": api_key_hash,
                    "updated_at": datetime.utcnow(),
                    "last_active": datetime.utcnow(),
                    "active": True,
                    "status": "active"
                }}
            )
            
            device_id = existing_device["device_id"]
            logger.info(f"Device updated: {device_id} for employee {employee_id}")
        else:
            # Save device in database
            device_data = {
                "device_id": device_id,
                "employee_id": employee_id,
                "device_name": device_name,
                "device_type": device_type,
                "api_key": api_key,  # Store plain API key for direct comparison
                "api_key_hash": api_key_hash,
                "registered_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "active": True,  # Make sure device is marked as active
                "status": "active"
            }
            
            # Save to the database
            devices_collection.insert_one(device_data)
            logger.info(f"Device registered: {device_id} for employee {employee_id}")
        
        # Do a verification test to ensure the API key works
        try:
            from app.core.security.auth import hash_api_key as verify_hash
            test_hash = verify_hash(api_key)
            logger.debug(f"Verification test - API Key: {api_key[:4]}...{api_key[-4:]}, Hash: {test_hash[:4]}...{test_hash[-4:]}")
            
            # Try to retrieve the device with the key
            found = devices_collection.find_one({"api_key": api_key})
            if found:
                logger.debug(f"Verification passed - device can be found with API key")
            else:
                logger.warning(f"Verification failed - device cannot be found with API key!")
        except Exception as ve:
            logger.error(f"Error during verification test: {str(ve)}")
        
        # Return the device ID and API key
        return {
            "device_id": device_id,
            "api_key": api_key,
            "message": "Device registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred registering the device"
        )
