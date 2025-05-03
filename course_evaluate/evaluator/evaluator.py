from ..agent.llm import LLM_API, LLM_Settings
from ..logger.logger import Logger
class Evaluator:
    def __init__(self, course_name, comments):
        logger = Logger()
        settings = LLM_Settings()
        llm = LLM_API(settings, logger)

        messages = [{"role": "system", "content": "你是一个AI助手，请根据评论给课程打分,根据上述评价,从给分,教学质量角度,从0到10给课程打分,请以如下形式回答问题'Point: Reason1: Reason2' "}]            
        try:

            messages.append({"role": "user", "content": comments})
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

    


