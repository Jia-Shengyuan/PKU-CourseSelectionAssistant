import asyncio
from agent.llm import LLM, LLM_Settings, AsyncLLM, AgentLLM
from agent.logger.logger import Logger
from typing import List
from rich.markdown import Markdown

def normal_chat():

    logger = Logger()
    settings = LLM_Settings(model_name="Pro/deepseek-ai/DeepSeek-R1")
    llm = LLM(settings, logger)

    messages = [{"role": "system", "content": "你是一个AI助手，请回答用户的问题。"}]

    
    while True:

        user_input = input("\n请输入您的问题（输入'quit'退出）: ")
        if user_input.lower() == 'quit':
            break
            
        try:

            messages.append({"role": "user", "content": user_input})
            response = llm.chat(messages)
                
            full_response = ""
            logger.log("AI回复: ")

            for token in response:
                logger.log(token, end="")
                full_response += token

            logger.log("")

            messages.append({"role": "assistant", "content": full_response})


        except Exception as e:
            logger.log_error(e)

async def async_chat(queries : List[str], display_while_running : bool = False):

    logger = Logger()
    settings = LLM_Settings()
    llm = AgentLLM(settings, logger)

    results = []

    async def single_chat(query : str):
        
        messages = [{"role": "system", "content": "你是一个AI助手，请回答用户的问题。"},
                    {"role": "user", "content": query}]
        
        try:

            response_generator = llm.chat(messages)
            full_response = ""
            if display_while_running:
                logger.log("AI回复: ")

            async for token in response_generator:
                if display_while_running:
                    logger.log(token, end="")
                full_response += token

            if display_while_running:
                logger.log("")
            results.append(full_response)

        except Exception as e:
            logger.log_error(e)

    tasks = [single_chat(query) for query in queries]
    await asyncio.gather(*tasks)

    logger.log_info("All task completed. Here are the results:")

    for result in results:
        logger.log_info("\nResult:")
        logger.log(Markdown(result))

def main():
    normal_chat()
    # asyncio.run(async_chat(["1+2+...+10=?", "1+2+4+...+128=?", "1+1/2+1/4+...=?"]))       

if __name__ == "__main__":
    main()
