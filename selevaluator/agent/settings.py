import json
from typing import Optional, Literal

class LLM_Settings:

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: Optional[bool] = None,
        model_type: Literal["evaluate", "gen_plan", "default"] = "default"
    ):
        
        json_config = json.load(open("config/config.json", "r", encoding="utf-8"))["model"]
        
        if model_type == "default":
            if (not model_name) or (not temperature) or (not top_p):
                raise ValueError("For default model type, model_name, temperature, and top_p must be provided.")
        
        self.base_url = base_url or json_config["base_url"]
        self.api_key = api_key or json_config["api_key"]
        self.model_name = model_name or json_config[model_type + "_model"]["name"]
        self.temperature = temperature or json_config[model_type + "_model"]["temperature"]
        self.top_p = top_p or json_config[model_type + "_model"]["top_p"]
        self.stream = stream if stream is not None else json_config.get("stream", True)
        