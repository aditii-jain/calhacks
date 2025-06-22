from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import time
from datetime import datetime

from models import (
    ClassifiedDataBatch,
    ClassifiedDataInput,
    StorageResponse,
    ClassifiedDataResponse,
    HealthResponse,
    StoredClassifiedData,
    DataFilter,
    InformativeLabel,
    HumanitarianLabel,
    DamageLabel
)
from database import db_service

router = APIRouter()

@router.post("/classified-data/store", response_model=StorageResponse)
async def store_classified_data(batch: ClassifiedDataBatch):
    """
    Store a batch of classified data
    """
    try:
        # Store all classified data
        stored_count = await db_service.store_classified_data_batch(batch.data)
        
        return StorageResponse(
            stored_count=stored_count,
            message=f"Successfully stored {stored_count} classified data records"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

@router.get("/classified-data/all", response_model=ClassifiedDataResponse)
async def get_all_classified_data():
    """Get all stored classified data"""
    try:
        all_data = await db_service.get_all_classified_data()
        
        return ClassifiedDataResponse(
            data=all_data,
            total_count=len(all_data),
            filter_applied="all classified data"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@router.get("/classified-data/filter", response_model=ClassifiedDataResponse)
async def get_filtered_classified_data(
    text_info: Optional[List[str]] = Query(None, description="Filter by text informative labels"),
    image_info: Optional[List[str]] = Query(None, description="Filter by image informative labels"),
    text_human: Optional[List[str]] = Query(None, description="Filter by text humanitarian labels"),
    image_human: Optional[List[str]] = Query(None, description="Filter by image humanitarian labels"),
    image_damage: Optional[List[str]] = Query(None, description="Filter by image damage labels"),
    min_text_conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum text confidence"),
    min_image_conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum image confidence"),
    has_image: Optional[bool] = Query(None, description="Filter by presence of image"),
    has_location: Optional[bool] = Query(None, description="Filter by presence of location")
):
    """Get filtered classified data based on various criteria"""
    try:
        # Convert string lists to enum lists
        text_info_enums = None
        if text_info:
            try:
                text_info_enums = [InformativeLabel(label) for label in text_info]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid text_info value: {e}")
        
        image_info_enums = None
        if image_info:
            try:
                image_info_enums = [InformativeLabel(label) for label in image_info]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid image_info value: {e}")
        
        text_human_enums = None
        if text_human:
            try:
                text_human_enums = [HumanitarianLabel(label) for label in text_human]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid text_human value: {e}")
        
        image_human_enums = None
        if image_human:
            try:
                image_human_enums = [HumanitarianLabel(label) for label in image_human]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid image_human value: {e}")
        
        image_damage_enums = None
        if image_damage:
            try:
                image_damage_enums = [DamageLabel(label) for label in image_damage]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid image_damage value: {e}")
        
        # Create filter
        data_filter = DataFilter(
            text_info=text_info_enums,
            image_info=image_info_enums,
            text_human=text_human_enums,
            image_human=image_human_enums,
            image_damage=image_damage_enums,
            min_text_conf=min_text_conf,
            min_image_conf=min_image_conf,
            has_image=has_image,
            has_location=has_location
        )
        
        # Apply filter
        filtered_data = await db_service.get_filtered_classified_data(data_filter)
        
        # Build filter description
        filter_parts = []
        if text_info_enums:
            filter_parts.append(f"text_info in {[e.value for e in text_info_enums]}")
        if image_info_enums:
            filter_parts.append(f"image_info in {[e.value for e in image_info_enums]}")
        if text_human_enums:
            filter_parts.append(f"text_human in {[e.value for e in text_human_enums]}")
        if image_human_enums:
            filter_parts.append(f"image_human in {[e.value for e in image_human_enums]}")
        if image_damage_enums:
            filter_parts.append(f"image_damage in {[e.value for e in image_damage_enums]}")
        if min_text_conf:
            filter_parts.append(f"text_conf >= {min_text_conf}")
        if min_image_conf:
            filter_parts.append(f"image_conf >= {min_image_conf}")
        if has_image is not None:
            filter_parts.append(f"has_image = {has_image}")
        if has_location is not None:
            filter_parts.append(f"has_location = {has_location}")
        
        filter_description = " AND ".join(filter_parts) if filter_parts else "no filters"
        
        return ClassifiedDataResponse(
            data=filtered_data,
            total_count=len(filtered_data),
            filter_applied=filter_description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtering failed: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health"""
    try:
        db_health = await db_service.health_check()
        record_count = await db_service.get_data_count()
        
        return HealthResponse(
            database_connected=db_health.get("database_connected", False),
            total_records_stored=record_count
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            total_records_stored=0
        )

 