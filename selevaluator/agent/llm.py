from openai import OpenAI, AsyncOpenAI
import openai
from .settings import LLM_Settings
import json
from typing import List, Dict, Generator, AsyncGenerator, Optional
from .logger.logger import Logger
from abc import abstractmethod

class BaseLLM:

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
       
        # If settings is not provided, then read from config.json
        if settings is None:
            settings = LLM_Settings()
            config = json.load(open("config/config.json", "r"))["model"]
            settings.model_name = config["model_name"]
            settings.base_url = config["base_url"]
            settings.api_key = config["api_key"]
            # temperature, top_p, stream are optional in config.json
            settings.temperature = config.get("temperature", settings.temperature)
            settings.top_p = config.get("top_p", settings.top_p)
            settings.stream = config.get("stream", settings.stream)

        self.logger = logger or Logger()

        if not settings.model_name:
            self.logger.log_error("Model name is empty!")
            return
        
        if not settings.base_url:
            self.logger.log_error("Base URL is empty!")
            return
        
        if not settings.api_key:
            self.logger.log_error("API key is empty!")
            return
        
        self.logger.log_info(f'url = "{settings.base_url}", model = {settings.model_name}, stream = {settings.stream}')

        self.settings = settings
        self.client : OpenAI | AsyncOpenAI = None

    @abstractmethod
    def chat(self, messages : List[Dict[str, str]]) -> Generator[str, None, None] | AsyncGenerator[str, None]:
        pass

class LLM(BaseLLM):

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
        super().__init__(settings, logger)
        self.client = OpenAI(
            base_url = settings.base_url,
            api_key = settings.api_key
        )

    def chat(self, messages : List[Dict[str, str]]) -> Generator[str, None, None]:

        try:
            response = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                temperature=self.settings.temperature,
                top_p=self.settings.top_p,
                stream=self.settings.stream
            )

            if self.settings.stream:
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
                
        except openai.AuthenticationError as e:
            self.logger.log_error(e)
            return "Error: Invalid API key"
        except Exception as e:
            self.logger.log_error(e)
            return "Error: Unable to chat with LLM"
                

class AsyncLLM(BaseLLM):

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
        super().__init__(settings, logger)
        self.client = AsyncOpenAI(
            base_url = settings.base_url,
            api_key = settings.api_key
        )

    async def chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                temperature=self.settings.temperature,
                top_p=self.settings.top_p,
                stream=self.settings.stream
            )
    
            if self.settings.stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except openai.AuthenticationError as e:
            self.logger.log_error(e)
            yield "Error: Invalid API key"
        except Exception as e:
            self.logger.log_error(e)
            yield "Error: Unable to chat with LLM"