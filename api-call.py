import requests
from rich.markdown import Markdown
from rich.console import Console
from rich.prompt import Prompt

# 配置信息
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "API-Key here"
model = "deepseek-ai/DeepSeek-V3"

console = Console()
messages = []

def chat_completion(messages):
    # """调用API: https://siliconflow.cn/zh-cn/models"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
        "response_format": {"type": "text"}
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        console.print(f"[bold red]API请求失败: {str(e)}[/]")
        return None

def main():
    console.print("[bold green]对话已开始，输入 'exit' 结束对话[/]")
    
    while True:
        user_input = Prompt.ask("[bold cyan]你的问题[/]")
        
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        messages.append({"role": "user", "content": user_input})
        
        console.print("[italic yellow]思考中...[/]")
        response = chat_completion(messages)
        
        if response:
            messages.append({"role": "assistant", "content": response})
            
            console.print("\n[bold magenta]回答:[/]")
            console.print(Markdown(response))
            console.print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()