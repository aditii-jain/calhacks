"""Database service layer for Crisis-MMD backend - Classified Data Management"""

from typing import List, Optional
from datetime import datetime
import logging

from supabase import create_client, Client
from config import settings
from models import (
    StoredClassifiedData, 
    ClassifiedDataInput, 
    InformativeLabel, 
    HumanitarianLabel, 
    DamageLabel,
    DataFilter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service supporting both mock and Supabase storage for classified data"""
    
    def __init__(self):
        self.use_supabase = settings.use_supabase
        self.mock_database: List[StoredClassifiedData] = []
        self.supabase_client: Optional[Client] = None
        
        if self.use_supabase:
            self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            if not settings.supabase_url or not settings.supabase_service_key:
                logger.error("Supabase credentials not configured")
                raise ValueError("Missing Supabase credentials")
            
            self.supabase_client = create_client(
                settings.supabase_url, 
                settings.supabase_service_key  # Use service key for server operations
            )
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    async def store_classified_data_batch(self, data_batch: List[ClassifiedDataInput]) -> int:
        """Store a batch of classified data"""
        
        if self.use_supabase:
            return await self._store_classified_data_supabase(data_batch)
        else:
            return await self._store_classified_data_mock(data_batch)
    
    async def _store_classified_data_mock(self, data_batch: List[ClassifiedDataInput]) -> int:
        """Store classified data in mock database"""
        stored_count = 0
        timestamp = datetime.now()
        
        for data_item in data_batch:
            stored_data = StoredClassifiedData(
                id=len(self.mock_database) + 1,
                tweet_id=data_item.tweet_id,
                image_id=data_item.image_id,
                text_info=data_item.text_info,
                text_info_conf=data_item.text_info_conf,
                image_info=data_item.image_info,
                image_info_conf=data_item.image_info_conf,
                text_human=data_item.text_human,
                text_human_conf=data_item.text_human_conf,
                image_human=data_item.image_human,
                image_human_conf=data_item.image_human_conf,
                image_damage=data_item.image_damage,
                image_damage_conf=data_item.image_damage_conf,
                tweet_text=data_item.tweet_text,
                image_url=data_item.image_url,
                image_path=data_item.image_path,
                location=data_item.location,
                created_at=timestamp,
                updated_at=timestamp
            )
            
            self.mock_database.append(stored_data)
            stored_count += 1
        
        logger.info(f"Stored {stored_count} classified data records in mock database")
        return stored_count
    
    async def _store_classified_data_supabase(self, data_batch: List[ClassifiedDataInput]) -> int:
        """Store classified data in Supabase database"""
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
        
        timestamp = datetime.now()
        data_records = []
        
        # Prepare data records
        for data_item in data_batch:
            record = {
                "tweet_id": data_item.tweet_id,
                "image_id": data_item.image_id,
                "text_info": data_item.text_info.value,
                "text_info_conf": float(data_item.text_info_conf),
                "image_info": data_item.image_info.value if data_item.image_info else None,
                "image_info_conf": float(data_item.image_info_conf) if data_item.image_info_conf else None,
                "text_human": data_item.text_human.value if data_item.text_human else None,
                "text_human_conf": float(data_item.text_human_conf) if data_item.text_human_conf else None,
                "image_human": data_item.image_human.value if data_item.image_human else None,
                "image_human_conf": float(data_item.image_human_conf) if data_item.image_human_conf else None,
                "image_damage": data_item.image_damage.value if data_item.image_damage else None,
                "image_damage_conf": float(data_item.image_damage_conf) if data_item.image_damage_conf else None,
                "tweet_text": data_item.tweet_text,
                "image_url": data_item.image_url,
                "image_path": data_item.image_path,
                "location": data_item.location,
                "created_at": timestamp.isoformat(),
                "updated_at": timestamp.isoformat()
            }
            data_records.append(record)
        
        try:
            # Insert classified data
            response = self.supabase_client.table("classified_data").insert(data_records).execute()
            stored_count = len(response.data) if response.data else 0
            
            logger.info(f"Stored {stored_count} classified data records in Supabase")
            return stored_count
            
        except Exception as e:
            logger.error(f"Failed to store classified data in Supabase: {e}")
            raise
    
    async def get_all_classified_data(self) -> List[StoredClassifiedData]:
        """Get all stored classified data"""
        
        if self.use_supabase:
            return await self._get_all_classified_data_supabase()
        else:
            return await self._get_all_classified_data_mock()
    
    async def _get_all_classified_data_mock(self) -> List[StoredClassifiedData]:
        """Get all classified data from mock database"""
        return self.mock_database.copy()
    
    async def _get_all_classified_data_supabase(self) -> List[StoredClassifiedData]:
        """Get all classified data from Supabase"""
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
        
        try:
            response = self.supabase_client.table("classified_data").select("*").order("created_at", desc=True).execute()
            
            data_list = []
            for record in response.data:
                data_item = StoredClassifiedData(
                    id=record["id"],
                    tweet_id=record["tweet_id"],
                    image_id=record["image_id"],
                    text_info=InformativeLabel(record["text_info"]),
                    text_info_conf=record["text_info_conf"],
                    image_info=InformativeLabel(record["image_info"]) if record["image_info"] else None,
                    image_info_conf=record["image_info_conf"],
                    text_human=HumanitarianLabel(record["text_human"]) if record["text_human"] else None,
                    text_human_conf=record["text_human_conf"],
                    image_human=HumanitarianLabel(record["image_human"]) if record["image_human"] else None,
                    image_human_conf=record["image_human_conf"],
                    image_damage=DamageLabel(record["image_damage"]) if record["image_damage"] else None,
                    image_damage_conf=record["image_damage_conf"],
                    tweet_text=record["tweet_text"],
                    image_url=record["image_url"],
                    image_path=record["image_path"],
                    location=record["location"],
                    created_at=datetime.fromisoformat(record["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(record["updated_at"].replace('Z', '+00:00'))
                )
                data_list.append(data_item)
            
            return data_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve classified data from Supabase: {e}")
            raise
    
    async def get_filtered_classified_data(self, data_filter: DataFilter) -> List[StoredClassifiedData]:
        """Get classified data with applied filters"""
        
        if self.use_supabase:
            return await self._get_filtered_classified_data_supabase(data_filter)
        else:
            return await self._get_filtered_classified_data_mock(data_filter)
    
    async def _get_filtered_classified_data_mock(self, data_filter: DataFilter) -> List[StoredClassifiedData]:
        """Get filtered classified data from mock database"""
        filtered_data = self.mock_database.copy()
        
        # Apply text_info filter
        if data_filter.text_info:
            filtered_data = [d for d in filtered_data if d.text_info in data_filter.text_info]
        
        # Apply image_info filter
        if data_filter.image_info:
            filtered_data = [d for d in filtered_data if d.image_info and d.image_info in data_filter.image_info]
        
        # Apply text_human filter
        if data_filter.text_human:
            filtered_data = [d for d in filtered_data if d.text_human and d.text_human in data_filter.text_human]
        
        # Apply image_human filter
        if data_filter.image_human:
            filtered_data = [d for d in filtered_data if d.image_human and d.image_human in data_filter.image_human]
        
        # Apply image_damage filter
        if data_filter.image_damage:
            filtered_data = [d for d in filtered_data if d.image_damage and d.image_damage in data_filter.image_damage]
        
        # Apply confidence thresholds
        if data_filter.min_text_conf:
            filtered_data = [d for d in filtered_data if d.text_info_conf >= data_filter.min_text_conf]
        
        if data_filter.min_image_conf:
            filtered_data = [d for d in filtered_data if d.image_info_conf and d.image_info_conf >= data_filter.min_image_conf]
        
        # Apply has_image filter
        if data_filter.has_image is not None:
            if data_filter.has_image:
                filtered_data = [d for d in filtered_data if d.image_url is not None]
            else:
                filtered_data = [d for d in filtered_data if d.image_url is None]
        
        # Apply has_location filter
        if data_filter.has_location is not None:
            if data_filter.has_location:
                filtered_data = [d for d in filtered_data if d.location is not None]
            else:
                filtered_data = [d for d in filtered_data if d.location is None]
        
        return filtered_data
    
    async def _get_filtered_classified_data_supabase(self, data_filter: DataFilter) -> List[StoredClassifiedData]:
        """Get filtered classified data from Supabase"""
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
        
        try:
            query = self.supabase_client.table("classified_data").select("*")
            
            # Apply filters
            if data_filter.text_info:
                text_info_values = [label.value for label in data_filter.text_info]
                query = query.in_("text_info", text_info_values)
            
            if data_filter.image_info:
                image_info_values = [label.value for label in data_filter.image_info]
                query = query.in_("image_info", image_info_values)
            
            if data_filter.text_human:
                text_human_values = [label.value for label in data_filter.text_human]
                query = query.in_("text_human", text_human_values)
            
            if data_filter.image_human:
                image_human_values = [label.value for label in data_filter.image_human]
                query = query.in_("image_human", image_human_values)
            
            if data_filter.image_damage:
                image_damage_values = [label.value for label in data_filter.image_damage]
                query = query.in_("image_damage", image_damage_values)
            
            if data_filter.min_text_conf:
                query = query.gte("text_info_conf", data_filter.min_text_conf)
            
            if data_filter.min_image_conf:
                query = query.gte("image_info_conf", data_filter.min_image_conf)
            
            if data_filter.has_image is not None:
                if data_filter.has_image:
                    query = query.not_.is_("image_url", "null")
                else:
                    query = query.is_("image_url", "null")
            
            if data_filter.has_location is not None:
                if data_filter.has_location:
                    query = query.not_.is_("location", "null")
                else:
                    query = query.is_("location", "null")
            
            response = query.order("created_at", desc=True).execute()
            
            data_list = []
            for record in response.data:
                data_item = StoredClassifiedData(
                    id=record["id"],
                    tweet_id=record["tweet_id"],
                    image_id=record["image_id"],
                    text_info=InformativeLabel(record["text_info"]),
                    text_info_conf=record["text_info_conf"],
                    image_info=InformativeLabel(record["image_info"]) if record["image_info"] else None,
                    image_info_conf=record["image_info_conf"],
                    text_human=HumanitarianLabel(record["text_human"]) if record["text_human"] else None,
                    text_human_conf=record["text_human_conf"],
                    image_human=HumanitarianLabel(record["image_human"]) if record["image_human"] else None,
                    image_human_conf=record["image_human_conf"],
                    image_damage=DamageLabel(record["image_damage"]) if record["image_damage"] else None,
                    image_damage_conf=record["image_damage_conf"],
                    tweet_text=record["tweet_text"],
                    image_url=record["image_url"],
                    image_path=record["image_path"],
                    location=record["location"],
                    created_at=datetime.fromisoformat(record["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(record["updated_at"].replace('Z', '+00:00'))
                )
                data_list.append(data_item)
            
            return data_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve filtered classified data from Supabase: {e}")
            raise
    
    async def get_data_count(self) -> int:
        """Get total count of classified data records"""
        
        if self.use_supabase:
            return await self._get_data_count_supabase()
        else:
            return len(self.mock_database)
    
    async def _get_data_count_supabase(self) -> int:
        """Get classified data count from Supabase"""
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
        
        try:
            response = self.supabase_client.table("classified_data").select("id", count="exact").execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Failed to get data count from Supabase: {e}")
            return 0
    
    async def get_users_by_city(self, city_name: str) -> List[dict]:
        """Get all active users in a specific city for emergency calling"""
        
        if self.use_supabase:
            return await self._get_users_by_city_supabase(city_name)
        else:
            return await self._get_users_by_city_mock(city_name)
    
    async def _get_users_by_city_mock(self, city_name: str) -> List[dict]:
        """Get users by city from mock database"""
        # For mock implementation, return empty list since we don't have users yet
        logger.info(f"Mock: Would get users for city '{city_name}'")
        return []
    
    async def _get_users_by_city_supabase(self, city_name: str) -> List[dict]:
        """Get users by city from Supabase"""
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
        
        try:
            # Query users where location.address contains the city name and user is active
            response = self.supabase_client.table("users").select(
                "id, name, phone_number, location, emergency_contacts"
            ).eq("is_active", True).ilike("location->>address", f"%{city_name}%").execute()
            
            users = []
            for record in response.data:
                user_data = {
                    "id": record["id"],
                    "name": record["name"],
                    "phone_number": record["phone_number"],
                    "location": record["location"],
                    "emergency_contacts": record["emergency_contacts"]
                }
                users.append(user_data)
            
            logger.info(f"Found {len(users)} active users in city '{city_name}'")
            return users
            
        except Exception as e:
            logger.error(f"Failed to get users by city from Supabase: {e}")
            raise
    
    async def health_check(self) -> dict:
        """Perform health check on database service"""
        
        if self.use_supabase:
            return await self._supabase_health_check()
        else:
            return {
                "database_connected": True,
                "database_type": "mock",
                "total_records_stored": len(self.mock_database)
            }
    
    async def _supabase_health_check(self) -> dict:
        """Perform health check on Supabase connection"""
        try:
            if not self.supabase_client:
                return {
                    "database_connected": False,
                    "database_type": "supabase",
                    "error": "Client not initialized"
                }
            
            # Try to get count of records
            total_count = await self._get_data_count_supabase()
            
            return {
                "database_connected": True,
                "database_type": "supabase",
                "total_records_stored": total_count
            }
            
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return {
                "database_connected": False,
                "database_type": "supabase",
                "error": str(e)
            }

# Global database service instance
db_service = DatabaseService()

def get_supabase_client():
    """Get the Supabase client instance from the global database service"""
    if not db_service.use_supabase:
        raise RuntimeError("Supabase is not enabled")
    if not db_service.supabase_client:
        raise RuntimeError("Supabase client not initialized")
    return db_service.supabase_client 