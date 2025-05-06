import json
import course_evaluate.evaluator.evaluator as evaluator
import sys

def main():
    evaluator.evaluate_json_file("course_evaluate\comments_1.json")
    evaluator.evaluate_json_file("course_evaluate\comments_2.json")
    evaluator.evaluate_json_file("course_evaluate\comments_3.json")


if __name__ == "__main__":
    main()
