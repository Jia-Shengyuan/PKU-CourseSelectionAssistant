def remove_duplicates_and_filter_lines(input_file, output_file):
    # 读取输入文件的内容
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # 使用集合去重
    unique_lines = set(lines)
    
    # 筛选出每行字符数大于l的行
    for l in range(50, 1000):
        filtered_lines = [line for line in unique_lines if len(line.strip()) > l and len(line.strip()) < 150]
        if len(filtered_lines) < 30:
            break
    
    # 将去重并筛选后的内容写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in filtered_lines:
            file.write(line)
            file.write('\n')

# 示例使用
input_file = 'result.txt'  # 输入文件路径
output_file = 'output.txt'  # 输出文件路径
remove_duplicates_and_filter_lines(input_file, output_file)
