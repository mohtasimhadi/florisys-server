from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Optional, Any
import os, json

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "florisys"
    files_dir: str = "./data/plots"
    cors_origins: List[AnyHttpUrl] = []
    max_upload_mb: int = 512
    backend_public_url: Optional[AnyHttpUrl] = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> Any:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            if s.startswith("["):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    pass  # fall through to comma split
            return [x.strip() for x in s.split(",") if x.strip()]
        return v

    @field_validator("backend_public_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

settings = Settings()
os.makedirs(settings.files_dir, exist_ok=True)
