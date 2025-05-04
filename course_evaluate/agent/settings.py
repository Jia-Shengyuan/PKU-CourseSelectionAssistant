import json
from typing import Optional


class LLM_Settings:

    def __init__(
        self,
        model_name : Optional[str] = None,
        base_url : Optional[str] = None,
        api_key : Optional[str] = None,
        temperature : Optional[float] = None,
        top_p : Optional[float] = None,
        stream : Optional[bool] = None
    ):
        
        json_config = json.load(open("config/config.example.json", "r", encoding="utf-8"))["model"]
        self.model_name = model_name or json_config["model_name"]
        self.base_url = base_url or json_config["base_url"]
        self.api_key = api_key or json_config["api_key"]
        self.temperature = temperature or json_config.get("temperature", 0.7)
        self.top_p = top_p or json_config.get("top_p", 1.0)
        self.stream = stream if stream is not None else json_config.get("stream", True)
        