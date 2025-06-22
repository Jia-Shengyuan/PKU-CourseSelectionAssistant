from pydantic import BaseModel
from typing import Optional, Dict, Any

CONFIG_PATH = "config/config.json"

class ConfigData(BaseModel):
    model: Dict[str, Any]
    user: Dict[str, Any]
    course: Dict[str, Any]
    crawler: Dict[str, Any]

class ModelConfig(BaseModel):
    name: str
    temperature: float
    top_p: float