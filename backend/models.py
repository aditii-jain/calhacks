from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import re

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

# === USER MODELS ===
class Location(BaseModel):
    """User location information"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate") 
    address: str = Field(..., min_length=1, description="Human-readable address")

class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str = Field(..., min_length=1, description="Contact person's name")
    phone: str = Field(..., description="Contact phone number")
    relationship: str = Field(..., min_length=1, description="Relationship to user (e.g., 'spouse', 'parent', 'friend')")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Basic phone validation - international format
        phone_pattern = r'^\+?[1-9]\d{8,14}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Phone number must be in international format with 9-15 digits (e.g., +1234567890)')
        return v

class UserInput(BaseModel):
    """Input model for user registration/update"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    phone_number: str = Field(..., description="Phone number in international format")
    location: Location = Field(..., description="User location")
    emergency_contacts: List[EmergencyContact] = Field(default=[], max_items=5, description="Emergency contacts (max 5)")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # International phone number validation
        phone_pattern = r'^\+?[1-9]\d{8,14}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Phone number must be in international format with 9-15 digits (e.g., +1234567890)')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    location: Optional[Location] = Field(None, description="User location")
    emergency_contacts: Optional[List[EmergencyContact]] = Field(None, max_items=5, description="Emergency contacts")
    is_active: Optional[bool] = Field(None, description="Whether user should receive alerts")

class StoredUser(BaseModel):
    """User data as stored in database"""
    id: str = Field(..., description="User UUID from Supabase Auth")
    name: str = Field(..., description="Full name")
    phone_number: str = Field(..., description="Phone number")
    location: Location = Field(..., description="User location")
    emergency_contacts: List[EmergencyContact] = Field(..., description="Emergency contacts")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# === AUTH MODELS ===
class PhoneAuthRequest(BaseModel):
    """Request for phone-based authentication"""
    phone_number: str = Field(..., description="Phone number for authentication")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        phone_pattern = r'^\+?[1-9]\d{8,14}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Phone number must be in international format with 9-15 digits')
        return v

class OTPVerificationRequest(BaseModel):
    """Request for OTP verification"""
    phone_number: str = Field(..., description="Phone number")
    otp_code: str = Field(..., min_length=4, max_length=8, description="OTP code received via SMS")
    user_profile: Optional[UserInput] = Field(None, description="User profile for registration")

class AuthResponse(BaseModel):
    """Response for authentication operations"""
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    user: Optional[StoredUser] = Field(None, description="User profile data")

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

class UserResponse(BaseModel):
    """Response for user operations"""
    success: bool = True
    user: Optional[StoredUser] = Field(None, description="User data")
    message: str = "Operation successful"

class UserListResponse(BaseModel):
    """Response for user list operations"""
    success: bool = True
    users: List[StoredUser] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    message: str = "Users retrieved successfully"

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    database_connected: bool = True
    total_records_stored: int = 0
    total_users_registered: int = 0

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

class UserFilter(BaseModel):
    """Filter options for querying users"""
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    location_radius: Optional[float] = Field(None, gt=0, description="Search radius in kilometers")
    center_lat: Optional[float] = Field(None, ge=-90, le=90, description="Center latitude for radius search")
    center_lng: Optional[float] = Field(None, ge=-180, le=180, description="Center longitude for radius search")

# === RED ZONE MODELS ===
class RedZoneTriggerRequest(BaseModel):
    """Request to trigger Red Zone emergency calling"""
    city: str = Field(..., min_length=1, description="City name where emergency occurred")
    incident_data: Dict[str, Any] = Field(..., description="Incident details for the calling agents")
    
class RedZoneTriggerResponse(BaseModel):
    """Response for Red Zone trigger operation"""
    success: bool = Field(..., description="Whether the trigger was successful")
    message: str = Field(..., description="Response message")
    affected_users_count: int = Field(..., description="Number of users that will be called")
    city: str = Field(..., description="City where emergency was triggered")
    agent_response: Optional[Dict[str, Any]] = Field(None, description="Response from calling agent")

 