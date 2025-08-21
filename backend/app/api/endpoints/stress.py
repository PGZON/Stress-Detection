from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Query, Body
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from app.schemas.schemas import StressSubmission, StressResponse
from app.models.models import create_stress_record
from app.core.security.deps import verify_device_api_key, limiter
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/record", response_model=StressResponse)
@limiter.limit("10/minute")
async def submit_stress_reading(
    submission: StressSubmission,
    request: Request,
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Any:
    """
    Submit a new stress reading from a device.
    API key can be provided either in X-Device-Key header or as api_key query parameter.
    """
    try:
        # Verify device_id and employee_id match with the submission
        device_id = device.get("device_id")
        employee_id = device.get("employee_id")
        
        if device_id != submission.device_id:
            logger.warning(f"Device ID mismatch in stress submission: {device_id} vs {submission.device_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device ID mismatch"
            )
        
        if employee_id != submission.employee_id:
            logger.warning(f"Employee ID mismatch in stress submission: {employee_id} vs {submission.employee_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID mismatch"
            )
        
        # Validate timestamp is not too far in the future
        try:
            # Convert submission timestamp to UTC datetime object
            submission_time = datetime.fromisoformat(submission.timestamp.replace('Z', '+00:00'))
            
            # Make sure we're working with timezone-aware objects
            import pytz
            utc = pytz.UTC
            
            # Create timezone-aware current time
            current_time = datetime.now(utc)
            
            # Create timezone-aware max future time
            max_future = current_time + timedelta(minutes=5)
            min_past = current_time - timedelta(hours=1)
            
            # Now we can safely compare timezone-aware objects
            if submission_time > max_future:
                logger.warning(f"Future timestamp in stress submission: {submission.timestamp}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Timestamp too far in future"
                )
                
            if submission_time < min_past:
                logger.warning(f"Past timestamp in stress submission: {submission.timestamp}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Timestamp too far in past"
                )
        except ValueError:
            logger.warning(f"Invalid timestamp format in stress submission: {submission.timestamp}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format. Use ISO-8601 format."
            )
        
        # Create stress record
        record = create_stress_record(submission)
        logger.info(f"Created stress record {record.record_id} for employee {employee_id}")
        
        return {"record_id": record.record_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing stress submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing the submission"
        )

@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_stress(
    request: Request,
    data: Dict[str, Any] = Body(...),
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Any:
    """
    Record a stress reading from a device.
    API key can be provided either in X-Device-Key header or as api_key query parameter.
    """
    try:
        # Get device and employee IDs from the authenticated device
        device_id = device.get("device_id")
        employee_id = device.get("employee_id")
        
        # Prepare stress reading data
        stress_data = {
            "reading_id": f"stress-{uuid.uuid4().hex[:8]}",
            "device_id": device_id,
            "employee_id": employee_id,
            "timestamp": datetime.utcnow(),
            "stress_level": data.get("stress_level"),
            "emotion": data.get("emotion"),
            "confidence": data.get("confidence"),
            "face_quality": data.get("face_quality", {}),
            "metadata": data.get("metadata", {})
        }
        
        # Save to the database
        from app.db.mongodb import stress_readings_collection
        stress_readings_collection.insert_one(stress_data)
        
        logger.info(f"Stress reading recorded: {stress_data['reading_id']} for employee {employee_id}")
        
        return {
            "reading_id": stress_data["reading_id"],
            "message": "Stress reading recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording stress reading: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred recording the stress reading"
        )
