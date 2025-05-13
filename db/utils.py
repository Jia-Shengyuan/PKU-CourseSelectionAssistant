import re

def normalize_name(name: str) -> str:
    roman_to_arabic = {
        "Ⅲ": "3",  "Ⅱ": "2", "Ⅰ": "1",
        "III": "3", "II": "2", "I": "1"
    }
    kanji_to_arabic = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
        "六": "6", "七": "7", "八": "8", "九" : "9", "十": "10",
    }
    # 去除括号、特殊字符、空格
    name = re.sub(r"[（）()【】《》\[\]{}、·\s]", "", name)
    # 替换罗马数字为阿拉伯数字
    for roman, arabic in roman_to_arabic.items():
        name = name.replace(roman, arabic)
    for kanji, arabic in kanji_to_arabic.items():
        name = name.replace(kanji, arabic)
    return name.lower()