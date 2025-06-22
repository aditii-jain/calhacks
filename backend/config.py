from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configuration for Crisis-MMD processing backend with Supabase integration"""
    
    # API Configuration
    app_name: str = "Crisis-MMD Processing API"
    version: str = "1.0.0"
    debug: bool = True
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///crisis_mmd.db"  # Fallback to SQLite
    use_supabase: bool = False  # Feature flag to switch between mock/supabase
    
    # Models Directory Communication
    models_service_url: str = "http://localhost:5000"
    models_timeout: int = 30
    
    # Processing Configuration
    seriousness_threshold: float = 0.7
    max_batch_size: int = 1000
    
    # Optional API Keys (for later integration)
    claude_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    class Config:
        env_file = [".env", "../.env", "../../.env"]  # Try multiple paths
        case_sensitive = False

# Global settings instance
settings = Settings() 