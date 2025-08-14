import pandas as pd
import asyncio
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from selevaluator.agent.llm import AsyncLLM, LLM_Settings
from selevaluator.agent.logger.logger import Logger
import json

class CourseDataProcessor:
    def __init__(self):
        self.logger = Logger()
        self.settings = LLM_Settings()
        self.llm = AsyncLLM(self.settings, self.logger)
        
    async def process_batch(self, df_batch, batch_index, start_index):
        """处理一批数据"""
        prompt = f"""请帮我处理以下课程信息列表，将其规范化为标准格式。
要求：
1. 将上课时间和地点分开
2. 如果信息在备注中，请提取到对应字段，只在备注中保留确实是备注的信息（习题课时间，考试时间等也算作备注信息）
3. 为老师添加姓名拼音缩写以方便检索，有多个老师时用逗号连接，格式形如"王福正/wfz（副教授)，高峡/gx（讲师）"，英文名字不添加缩写，形如"John Smith（助理教授）"即可
4. 保持其余原有信息不变，只做格式调整
5. 返回JSON数组格式，每个元素包含以下字段：
   - course_name: str，课程名称
   - course_id: int，课程编号
   - teacher: str，教师信息
   - class_id: int，班号
   - time: str，上课时间（格式：单周/每周+周几+第几节，如"每周周一1-2节"）
   - location: str，上课地点
   - credit: float，学分
   - note: str，备注
5. 对于没有给出的字符串，请返回空字符串

原始数据列表：
{df_batch.to_dict('records')}

请直接返回JSON数组格式的结果，不要有其他文字说明，也不要有```json```的处理，确保返回值可以直接被json.loads加载。"""

        messages = [
            {"role": "system", "content": "你是一个专门处理课程数据的助手。请将杂乱的课程信息整理成标准格式。"},
            {"role": "user", "content": prompt}
        ]

        try:
            self.logger.log_info(f"开始处理第{batch_index + 1}批数据...")
            response = ""
            async for token in self.llm.chat(messages):
                response += token
            
            # 解析JSON响应
            processed_data = json.loads(response)
            
            # 为每个处理后的数据添加原始索引
            for i, data in enumerate(processed_data):
                data['_original_index'] = start_index + i
                
            return processed_data

        except json.JSONDecodeError as e:
            self.logger.log_error(f"解析JSON响应时发生错误: {e}")
            with open(f"data/error_response/batch_{batch_index}.txt", "w", encoding="utf-8") as f:
                f.write(response)
            raise
        except Exception as e:
            self.logger.log_error(f"处理数据时发生错误: {e}")
            raise

    async def process_excel(self, input_file, output_file, batch_size=32, max_concurrent=16):
        """处理整个Excel文件，分批并行发送给大模型"""
        try:
            # 读取Excel文件
            df = pd.read_excel(input_file)
            total_rows = len(df)
            self.logger.log_info(f"成功读取Excel文件，共{total_rows}行数据，{((total_rows-1)//batch_size)+1}批数据")

            # 创建批次
            batches = []
            for i in range(0, total_rows, batch_size):
                df_batch = df.iloc[i:i+batch_size]
                batch_index = i // batch_size
                batches.append((df_batch, batch_index, i))  # 添加起始索引

            # 使用信号量控制并发数
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(batch):
                df_batch, batch_index, start_index = batch
                async with semaphore:
                    try:
                        return await self.process_batch(df_batch, batch_index, start_index)
                    except Exception as e:
                        self.logger.log_error(f"处理第{batch_index + 1}批数据时发生错误: {e}")
                        return []

            # 并行处理所有批次
            all_results = await asyncio.gather(
                *[process_with_semaphore(batch) for batch in batches],
                return_exceptions=True
            )

            # 合并结果
            all_processed_data = []
            for result in all_results:
                if isinstance(result, list):
                    all_processed_data.extend(result)
                else:
                    self.logger.log_error(f"处理批次时发生错误: {result}")

            if not all_processed_data:
                raise Exception("没有成功处理任何数据")

            # 按原始索引排序
            all_processed_data.sort(key=lambda x: x['_original_index'])
            
            # 移除临时索引字段
            for data in all_processed_data:
                data.pop('_original_index', None)

            # 保存JSON格式的结果
            with open("data/processed_courses.json", "w", encoding="utf-8") as f:
                json.dump(all_processed_data, f, ensure_ascii=False)

            # 创建新的DataFrame
            new_df = pd.DataFrame(all_processed_data)
            
            # 保存为新的Excel文件
            new_df.to_excel(output_file, index=False)
            self.logger.log_info(f"处理完成，共处理{len(all_processed_data)}条数据，结果已保存到{output_file}")

        except Exception as e:
            self.logger.log_error(f"处理Excel文件时发生错误: {e}")
            raise

async def main():
    processor = CourseDataProcessor()
    input_file = "data/2025-2026-1.xlsx"
    output_file = "data/2025-2026-1_processed.xlsx"
    # 可以调整batch_size和max_concurrent参数
    await processor.process_excel(input_file, output_file, batch_size=32, max_concurrent=40)

if __name__ == "__main__":
    asyncio.run(main())
