import sys
from bs4 import BeautifulSoup, Comment
from collections import defaultdict

def extract_visible_text(html_content):
    """提取HTML中的可见文本，用换行分隔不同内容块"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除不需要的标签
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    
    # 移除HTML注释
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # 按父元素分组文本节点
    parent_groups = defaultdict(list)
    for text_node in soup.find_all(text=True):
        # 检查是否在排除标签内
        if any(parent.name in {'script', 'style', 'noscript'} 
               for parent in text_node.parents):
            continue
        stripped = text_node.strip()
        if stripped:
            parent_groups[text_node.parent].append(stripped)
    
    # 合并同组文本并过滤空内容
    visible_blocks = [
        ' '.join(texts) 
        for texts in parent_groups.values() 
        if ''.join(texts).strip()
    ]
    
    return '\n'.join(visible_blocks)

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("使用方法: python html_text_extractor.py <输入文件.html>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html = f.read()
        result = extract_visible_text(html)
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(result)
        # print(result)
    except Exception as e:
        print(f"处理文件时出错: {e}")
        sys.exit(1)