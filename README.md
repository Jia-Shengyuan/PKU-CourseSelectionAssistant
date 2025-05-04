# PKU Course Selection Assistant

update 2025.4.24 by devout:

读取所需要的课程并在数据库查找的基础功能已经基本实现

# 文件信息

- `app.models` 和 `app.schemas` 下存储的是课程的格式规范，使用 Pydantic 实现，如果有需要 Pydantic 可以直接生成对应的 json 文件

- `app.crud` 下的 `course_crud.py` 中的各个函数可以实现对数据库的修改（增加和删除等）以及查询操作，后面单独查询某一门课程就是调用这里面的 `get_courses_by_name` 函数，支持对于括号、空格、汉字数字&罗马数字&阿拉伯数字的模糊匹配

- `app.db` 下存储的是数据库的相关信息，使用的是 SQLAlchemy 工具包，如果（万一）需要对db直接进行查询的话可以参考 `app/crud/course_crud.get_courses_by_name` 中的实现，需要 `from sqlalchemy.orm import Session`

- `scripts/import_course_from_excel.py` 是读取课程信息 Excel 并生成 db 的脚本，正常情况下应该无需调用。

- `scripts/search_in_pdf.py` 是读取pdf并转化成这学期要选的课程信息的脚本，正常情况下应该无需调用。

- `scripts/search_from_config.py` 是根据 `config/config.json` 的信息和 `config/plan.pdf` 的信息，在数据库中进行查找，并返回一个list包含课程的所有教室信息。

### 调用方法

```python
from scripts.search_from_config import get_courses

result = get_courses()
```

### 一些注意事项

- 现在培养方案pdf必须重命名为 `plan.pdf`

- `scripts/search_in_pdf.py` 依赖 `pdfplumber` 库，需要自行安装，或者运行 `pip install -r requirements.txt`

后续还需要进行一些输入预处理和异常处理机制的完善

# LLM 调用

- 先在 `config/config.json` 配置模型
- 之后可以在 `src` 文件夹中的 `chat_example.py` 可以用来测试
- 调用 `LLM_API` 的 `chat` 方法即可对话（ `achat` 未测试）

-------

# 树洞信息获取

update 2025.5.1 by zcxxnqwq:

已基本实现爬虫功能，devout 的课程列表的搜索结果在 `crawler/all_courses_search_results.html`中，可以用于后续步骤的处理。

目前的爬虫方式是每个课程搜了三条测评（为了方便调试），爬下来洞主的原帖子和全部评论，后续视需要和技术情况会尝试爬得更精简一点。

在慢慢修 login 和爬虫的衔接部分。由于一天只能 login 实验五次，这个战线可能有点长。

# 课程评分器

## 使用方法:
`import course_evaluate.evaluator.evaluator as evaluator` 
`evaluator.evaluate_jason_file("path_to_json_file")`

便可依据`course_evaluate/comments_X.json`文件生成`coure_reviews.json`文件
## 样例:
运行根目录下的`test_evaluator.py`


# 前端（UI）

## 项目结构
```
选课辅助系统/
├── ui/                # 前端项目目录
│   └── README.md     # [前端项目说明](./ui/README.md)
├── ...               # 其他目录
└── README.md         # 项目说明
```

## 前端项目
前端项目使用 Vue 3 + Element Plus 构建，详细说明请参见 [前端项目文档](./ui/README.md)。