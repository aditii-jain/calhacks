"""
User authentication and management routes for Crisis-MMD backend.
Handles phone-based authentication with Supabase Auth and user profile management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import json
from datetime import datetime

from models import (
    PhoneAuthRequest, OTPVerificationRequest, AuthResponse,
    UserInput, UserUpdate, StoredUser, UserResponse, UserListResponse,
    Location, EmergencyContact, UserFilter
)
from database import db_service
from config import settings

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

# === AUTHENTICATION ENDPOINTS ===

@router.post("/auth/send-otp", response_model=AuthResponse)
async def send_otp(request: PhoneAuthRequest):
    """
    Send OTP to phone number for authentication.
    This endpoint initiates phone-based authentication.
    """
    try:
        # In a real implementation, this would:
        # 1. Use Supabase Auth to send OTP via SMS
        # 2. Return success/failure status
        
        # For now, we'll simulate the OTP sending
        # TODO: Integrate with Supabase Auth client
        
        return AuthResponse(
            success=True,
            message=f"OTP sent to {request.phone_number}. Please check your SMS.",
            access_token=None,
            refresh_token=None,
            user=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@router.post("/auth/verify-otp", response_model=AuthResponse)
async def verify_otp(request: OTPVerificationRequest):
    """
    Verify OTP and complete authentication.
    For new users, also creates user profile.
    """
    try:
        # TODO: Verify OTP with Supabase Auth
        # For now, we'll simulate successful verification
        
        # Check if user exists
        existing_user = None
        if hasattr(db_service, 'get_user_by_phone'):
            existing_user = await db_service.get_user_by_phone(request.phone_number)
        
        if existing_user:
            # Existing user login
            return AuthResponse(
                success=True,
                message="Login successful",
                access_token="mock_access_token",  # TODO: Get real JWT from Supabase
                refresh_token="mock_refresh_token",
                user=existing_user
            )
        else:
            # New user registration
            if not request.user_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User profile required for new user registration"
                )
            
            # Create new user
            new_user = await create_user_profile(request.user_profile, "mock_user_id")
            
            return AuthResponse(
                success=True,
                message="Registration successful",
                access_token="mock_access_token",
                refresh_token="mock_refresh_token",
                user=new_user
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )

# === USER PROFILE ENDPOINTS ===

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the authenticated user's profile.
    """
    try:
        # TODO: Decode JWT token to get user ID
        user_id = "mock_user_id"  # Extract from JWT token
        
        user = await db_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            success=True,
            user=user,
            message="Profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update the authenticated user's profile.
    """
    try:
        # TODO: Decode JWT token to get user ID
        user_id = "mock_user_id"
        
        updated_user = await db_service.update_user(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            success=True,
            user=updated_user,
            message="Profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

# === ADMIN ENDPOINTS (Service Role Only) ===

@router.get("/", response_model=UserListResponse)
async def list_users(
    filter_params: UserFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    List users with optional filtering.
    Admin/Service role only.
    """
    try:
        # TODO: Verify service role from JWT
        
        users = await db_service.get_users(filter_params, skip, limit)
        total_count = await db_service.count_users(filter_params)
        
        return UserListResponse(
            success=True,
            users=users,
            total_count=total_count,
            message=f"Retrieved {len(users)} users"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.get("/location-radius", response_model=UserListResponse)
async def get_users_in_radius(
    center_lat: float,
    center_lng: float,
    radius_km: float,
    active_only: bool = True,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get users within a specific radius of a location.
    Used for crisis zone calling.
    """
    try:
        # TODO: Verify service role from JWT
        
        if radius_km <= 0 or radius_km > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Radius must be between 0 and 1000 km"
            )
        
        users = await db_service.get_users_in_radius(center_lat, center_lng, radius_km, active_only)
        
        return UserListResponse(
            success=True,
            users=users,
            total_count=len(users),
            message=f"Found {len(users)} users within {radius_km}km radius"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users in radius: {str(e)}"
        )

# === HELPER FUNCTIONS ===

async def create_user_profile(user_input: UserInput, auth_user_id: str) -> StoredUser:
    """
    Create a new user profile in the database.
    """
    # Convert location and emergency contacts to JSONB format
    location_json = user_input.location.model_dump()
    contacts_json = [contact.model_dump() for contact in user_input.emergency_contacts]
    
    user_data = {
        "id": auth_user_id,
        "name": user_input.name,
        "phone_number": user_input.phone_number,
        "location": location_json,
        "emergency_contacts": contacts_json,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    created_user = await db_service.create_user(user_data)
    return created_user

def extract_user_id_from_token(credentials: HTTPAuthorizationCredentials) -> str:
    """
    Extract user ID from JWT token.
    TODO: Implement proper JWT validation with Supabase.
    """
    # This is a placeholder - in real implementation:
    # 1. Validate JWT signature
    # 2. Check expiration
    # 3. Extract user ID from claims
    return "mock_user_id"

def verify_service_role(credentials: HTTPAuthorizationCredentials) -> bool:
    """
    Verify that the token has service role permissions.
    TODO: Implement proper role checking.
    """
    # This is a placeholder - in real implementation:
    # 1. Decode JWT token
    # 2. Check role claim
    # 3. Verify service role permissions
    return True 