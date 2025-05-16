import json
import course_evaluate.evaluator.evaluator as evaluator
import sys

def main():
    ls = {"人工智能基础","微电子与电路基础", "电磁学", "高等数学 B 二", "高等代数 II", "程序设计实习", "普通物理 Ⅰ"}
    evaluator.evaluate_course(ls)

if __name__ == "__main__":
    main()
