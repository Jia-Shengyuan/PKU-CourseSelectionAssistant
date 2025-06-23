from openai import OpenAI, AsyncOpenAI
import openai
from .settings import LLM_Settings
import json
from typing import List, Dict, Generator, AsyncGenerator, Optional, Callable, TypedDict, Literal
from .logger.logger import Logger
from abc import abstractmethod, ABC

class LLM_Response():
    def __init__(self, state: Literal["reasoning", "answering", "retrying", "error"], content: str):
        self.state = state
        self.content = content

class BaseLLM(ABC):

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
       
        # If settings is not provided, then read from config.json
        if settings is None:
            settings = LLM_Settings()
            config = json.load(open("config/config.json", "r", encoding='utf-8'))["model"]
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
    def chat(self, messages : List[Dict[str, str]], *args, **kwargs) -> Generator[LLM_Response, None, None] | AsyncGenerator[LLM_Response, None]:
        pass

class LLM(BaseLLM):

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
        super().__init__(settings, logger)
        self.client = OpenAI(
            base_url = settings.base_url,
            api_key = settings.api_key
        )

    def chat(self, messages : List[Dict[str, str]]) -> Generator[LLM_Response, None, None]:

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
                    if chunk.choices[0].delta.reasoning_content is not None:
                        yield LLM_Response(state = "reasoning", content = chunk.choices[0].delta.reasoning_content)
                    if chunk.choices[0].delta.content is not None:
                        yield LLM_Response(state = "answering", content = chunk.choices[0].delta.content)
                        # yield {"state": "answering", "content": chunk.choices[0].delta.content}
            else:
                if response.choices[0].message.reasoning_content is not None:
                    yield LLM_Response(state = "reasoning", content = response.choices[0].message.reasoning_content)
                    # yield {"state": "reasoning", "content": response.choices[0].message.reasoning_content}
                yield LLM_Response(state = "answering", content = response.choices[0].message.content)
                # yield {"state": "answering", "content": response.choices[0].message.content}
                
        except openai.AuthenticationError as e:
            self.logger.log_error(e)
            return LLM_Response(state = "error", content = "Invalid API key")
        except Exception as e:
            self.logger.log_error(e)
            return LLM_Response(state = "error", content = "Unable to chat with LLM, " + e)
            # return "Error: Unable to chat with LLM"
                

class AsyncLLM(BaseLLM):

    def __init__(self, settings : Optional[LLM_Settings] = None, logger : Optional[Logger] = None):
        super().__init__(settings, logger)
        self.client = AsyncOpenAI(
            base_url = settings.base_url,
            api_key = settings.api_key
        )

    async def chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[LLM_Response, None]:
        
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
                    if chunk.choices[0].delta.reasoning_content is not None:
                        yield LLM_Response(state="reasoning", content=chunk.choices[0].delta.reasoning_content)
                    if chunk.choices[0].delta.content is not None:
                        yield LLM_Response(state="answering", content=chunk.choices[0].delta.content)
            else:
                if response.choices[0].message.reasoning_content is not None:
                    yield LLM_Response(state="reasoning", content=response.choices[0].message.reasoning_content)
                yield LLM_Response(state="answering", content=response.choices[0].message.content)

        except openai.AuthenticationError as e:
            self.logger.log_error(e)
            yield LLM_Response(state = "error", content = "Error: Invalid API key")
        except Exception as e:
            self.logger.log_error(e)
            yield LLM_Response(state = "error", content = "Error: Unable to chat with LLM, " + e)
            # yield "Error: Unable to chat with LLM"

class AgentLLM(AsyncLLM):

    """
    An agent that checks for errors in the LLM response.
    If an error is detected, it will ask the LLM again, using error message as appendix context.
    Note that error checking will force the LLM to respond in a single turn,
    so the `stream` parameter in `LLM_Settings` will be ignored if error_checker is not None.
    """

    async def chat(
        self,
        messages: List[Dict[str, str]],
        error_checker: Optional[Callable[[str], List[str]]] = None,
        max_retries: int = 3,
    ) -> AsyncGenerator[LLM_Response, None]:

        # if no error_checker is provided, just use the base class chat method
        # and return the response as a stream (if required)    
        if error_checker is None:
            async for chunk in super().chat(messages):
                yield chunk
            return

        response_text = ""
        async for chunk in super().chat(messages):
            if chunk.state == "reasoning":
                yield chunk
            elif chunk.state == "answering":
                response_text += chunk.content

        for i in range(max_retries):

            errors = error_checker(response_text)

            if errors:
                self.logger.log_warning(f"检测到大模型回复的错误: {errors}")
                self.logger.log_info(f"大模型的原始回复为：{response_text}")
                self.logger.log_info("正在重新请求大模型...")

                yield LLM_Response(state="retrying", content="检测到输出内容不正确，正在重新请求大模型...")

                error_prompt = "请注意，你刚才的回复中，存在错误（不符合约定格式）的信息。请根据以下错误提示重新回答问题：\n" + "\n".join(errors) + "\n注意：你的新的回答需要符合约定格式，且不包含任何错误，不包含除json回复外的任何信息，确保你的回复能被json.loads()直接解析。同时，确保你将重点放在解决错误上，而不是其他地方。例如，如果你的错误是输出无法直接被json.loads()函数解析，那么你不应该去花时间纠结是否要修改具体内容；如果错误是课程时间冲突，那你也不必去检查其他课程的格式是否正确。"
                    
                messages.append({
                    "role": "assistant",
                    "content": response_text
                })                
                messages.append({
                    "role": "user",
                    "content": error_prompt
                })
                
                response_text = ""
                async for chunk in super().chat(messages):
                    if chunk.state == "reasoning":
                        yield chunk
                    elif chunk.state == "answering":
                        response_text += chunk.content

            else:
                self.logger.log_info("大模型回复没有错误")
                break

        # self.settings.stream = is_streaming  # Restore the original streaming setting
        yield LLM_Response(state="answering", content=response_text)
