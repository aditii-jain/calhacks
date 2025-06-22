from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

# Classification Labels (from CrisisMMD dataset)
class InformativeLabel(str, Enum):
    INFORMATIVE = "informative"
    NOT_INFORMATIVE = "not_informative"
    DONT_KNOW_OR_CANT_JUDGE = "dont_know_or_cant_judge"

class HumanitarianLabel(str, Enum):
    AFFECTED_INDIVIDUALS = "affected_individuals"
    INFRASTRUCTURE_AND_UTILITY_DAMAGE = "infrastructure_and_utility_damage"
    INJURED_OR_DEAD_PEOPLE = "injured_or_dead_people"
    MISSING_OR_FOUND_PEOPLE = "missing_or_found_people"
    RESCUE_VOLUNTEERING_OR_DONATION_EFFORT = "rescue_volunteering_or_donation_effort"
    VEHICLE_DAMAGE = "vehicle_damage"
    OTHER_RELEVANT_INFORMATION = "other_relevant_information"
    NOT_HUMANITARIAN = "not_humanitarian"

class DamageLabel(str, Enum):
    SEVERE_DAMAGE = "severe_damage"
    MILD_DAMAGE = "mild_damage"
    LITTLE_OR_NO_DAMAGE = "little_or_no_damage"
    DONT_KNOW_OR_CANT_JUDGE = "dont_know_or_cant_judge"

# === INPUT MODELS ===
class ClassifiedDataInput(BaseModel):
    """Input model for classified tweet data"""
    tweet_id: int = Field(..., description="Original Twitter tweet ID")
    image_id: str = Field(..., pattern=r"^[0-9]+_[0-9]+$", description="Tweet ID with image index (tweet_id_index)")
    
    # Text classification
    text_info: InformativeLabel = Field(..., description="Informative classification for tweet text")
    text_info_conf: float = Field(..., ge=0.0, le=1.0, description="Confidence score for text classification")
    
    # Image classification (optional)
    image_info: Optional[InformativeLabel] = Field(None, description="Informative classification for tweet image")
    image_info_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for image classification")
    
    # Text humanitarian classification (optional)
    text_human: Optional[HumanitarianLabel] = Field(None, description="Humanitarian classification for tweet text")
    text_human_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for text humanitarian classification")
    
    # Image humanitarian classification (optional)
    image_human: Optional[HumanitarianLabel] = Field(None, description="Humanitarian classification for tweet image")
    image_human_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for image humanitarian classification")
    
    # Image damage assessment (optional)
    image_damage: Optional[DamageLabel] = Field(None, description="Damage severity assessment for tweet image")
    image_damage_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for image damage assessment")
    
    # Tweet content
    tweet_text: str = Field(..., min_length=1, description="Original tweet text")
    image_url: Optional[str] = Field(None, description="URL of tweet image")
    image_path: Optional[str] = Field(None, description="Local path to tweet image")
    location: Optional[str] = Field(None, description="Location information")

class ClassifiedDataBatch(BaseModel):
    """Batch of classified data for processing"""
    data: List[ClassifiedDataInput] = Field(..., max_items=1000, description="List of classified tweet data")

# === DATABASE MODELS ===
class StoredClassifiedData(BaseModel):
    """Classified data stored in database"""
    model_config = {"protected_namespaces": ()}
    
    id: Optional[int] = Field(None, description="Database primary key")
    tweet_id: int = Field(..., description="Original Twitter tweet ID")
    image_id: str = Field(..., description="Tweet ID with image index")
    
    # Text classification
    text_info: InformativeLabel = Field(..., description="Text informative classification")
    text_info_conf: float = Field(..., description="Text classification confidence")
    
    # Image classification
    image_info: Optional[InformativeLabel] = Field(None, description="Image informative classification")
    image_info_conf: Optional[float] = Field(None, description="Image classification confidence")
    
    # Text humanitarian classification
    text_human: Optional[HumanitarianLabel] = Field(None, description="Text humanitarian classification")
    text_human_conf: Optional[float] = Field(None, description="Text humanitarian confidence")
    
    # Image humanitarian classification
    image_human: Optional[HumanitarianLabel] = Field(None, description="Image humanitarian classification")
    image_human_conf: Optional[float] = Field(None, description="Image humanitarian confidence")
    
    # Image damage assessment
    image_damage: Optional[DamageLabel] = Field(None, description="Image damage assessment")
    image_damage_conf: Optional[float] = Field(None, description="Image damage confidence")
    
    # Tweet content
    tweet_text: str = Field(..., description="Original tweet text")
    image_url: Optional[str] = Field(None, description="Tweet image URL")
    image_path: Optional[str] = Field(None, description="Local image path")
    location: Optional[str] = Field(None, description="Location information")
    
    # Metadata
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

# === RESPONSE MODELS ===
class StorageResponse(BaseModel):
    """Response for data storage operations"""
    success: bool = True
    stored_count: int = Field(..., description="Number of records stored")
    message: str = "Data stored successfully"

class ClassifiedDataResponse(BaseModel):
    """Response for classified data queries"""
    success: bool = True
    data: List[StoredClassifiedData] = Field(..., description="List of classified data")
    total_count: int = Field(..., description="Total number of records")
    filter_applied: Optional[str] = Field(None, description="Description of applied filters")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    database_connected: bool = True
    total_records_stored: int = 0

# === FILTER MODELS ===
class DataFilter(BaseModel):
    """Filter options for querying classified data"""
    text_info: Optional[List[InformativeLabel]] = Field(None, description="Filter by text informative labels")
    image_info: Optional[List[InformativeLabel]] = Field(None, description="Filter by image informative labels")
    text_human: Optional[List[HumanitarianLabel]] = Field(None, description="Filter by text humanitarian labels")
    image_human: Optional[List[HumanitarianLabel]] = Field(None, description="Filter by image humanitarian labels")
    image_damage: Optional[List[DamageLabel]] = Field(None, description="Filter by image damage labels")
    min_text_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum text confidence threshold")
    min_image_conf: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum image confidence threshold")
    has_image: Optional[bool] = Field(None, description="Filter by presence of image")
    has_location: Optional[bool] = Field(None, description="Filter by presence of location")

 