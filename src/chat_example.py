from agent.llm import LLM_API, LLM_Settings
from logger.logger import Logger

def main():

    logger = Logger()
    settings = LLM_Settings()
    llm = LLM_API(settings, logger)

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
            logger.log_error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
