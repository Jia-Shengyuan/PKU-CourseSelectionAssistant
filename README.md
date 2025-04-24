# PKU Course Selection Assistant

I have changed the name for this project, please clone it again.

`pre_process.py` is used to extract visible text from HTML content, you can try it with `test.html`. It seems to be that running that code will cause warnings, maybe you can ask AIs to fix it.

`api-call.py` is used to call the API of DeepSeek, note that you need to fill the API_KEY value in code before using it.

---

update 2025.4.24 by devout:

读取所需要的课程并在数据库查找的基础功能已经基本实现

### 文件信息

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