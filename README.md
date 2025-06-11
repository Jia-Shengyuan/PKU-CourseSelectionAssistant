# PKU Course Selection Assistant

## 项目概述

这是一个可以根据你提供的个人介绍、选课计划等信息，去自动爬取树洞课程评测，并通过大模型汇总，辅助选课的项目，免去了选课时同学们手工搜索树洞大量评测的麻烦。

你需要做的：

1. 将项目

## 环境配置

### Python环境配置
1. 安装 Python (开发环境为 3.12.7 版本)
   - 访问 [Python官网](https://www.python.org/) 下载并安装
   - 确保安装时将 Python 添加到系统环境变量

2. 安装依赖包：先在终端中进入本项目根目录，之后输入
   ```bash
   pip install -r requirements.txt
   ```

### 前端环境配置
1. 安装 Node.js
   - 访问 [Node.js 官网](https://nodejs.org/) 下载并安装
   - 建议安装 LTS（长期支持）版本
   - 确保安装时将Node.js添加到系统环境变量

2. 安装 pnpm
   ```bash
   npm install -g pnpm
   ```

3. 安装前端依赖（同样是先在终端中进入本项目根目录，之后再输入下方指令）
   ```bash
   cd ui
   pnpm install
   ```

## 项目运行

项目的运行需要同时启用前后端

启动后端：使用终端进入根目录后
```bash
uvicorn api.main:app --reload
```

启动前端（需要新开一个终端，后端的不关）：
```bash
cd ui
pnpm run dev
```

之后按照这个终端输出打开前端对应网页即可，默认情况下一般为 [http://localhost:5173/](http://localhost:5173/)。

打开前端网页后，根据前端配置选课信息，即可开始自动爬取评价并选课。其中唯一不能在前端完成的一步是配置你的培养方案，你需要将其命名为 `plan.pdf` 并放在项目根目录下的 `config` 文件夹中。

## 获取大模型 API Key

由于本项目需要通过大模型选课，你需要提供能够与大模型进行交互的 API Key 才能运行。

下面的教程基于[硅基流动](https://siliconflow.cn/)平台，其他平台获取 API Key 的教程可以去网上搜索。

硅基流动你也自己搜吧。

------

## LLM 调用

- 先在 `config/config.json` 配置模型
- 之后可以在 `src` 文件夹中的 `chat_example.py` 可以用来测试
- 调用 `LLM` 或 `AsyncLLM` 的 `chat` 方法即可对话，调用方法见 `chat_example.py`

-------

## 树洞信息获取

update 2025.5.9 by zcxxnqwq:

修了爬虫。实现了每门课的测评分别存储在一个 HTML 里，存储在 `crawler` 目录下。

只存登录 cookies 似乎因为反爬虫机制无法自动登录，以后的每次登录依然需要短信验证码。现采用从 Chrome 用户数据目录直接复用登录态的方法，`config.json` 新增 `chrome_user_data_dir` 用于让用户填写用户目录地址，目前我的电脑上不出错的方式是自己新建文件夹 `C:\Users\用户名\PKU-Chrome-Profile`，在 config 里填写这个路径，然后需要手动登录一次，使这个目录下存储登录状态，之后每次本设备访问树洞无需登录。

# 课程评分器

## 使用方法:
`import course_evaluate.evaluator.evaluator as evaluator` 
`evaluator.evaluate_course(ls)`

输出的课程评价在`crawler\data`目录下, 每次调用函数会清除该目录下的全部`json`文件

评价逐个老师进行

其中`ls`为课程名称列表, 如 `ls = {"人工智能基础","微电子与电路基础"}`

需要依赖`crawler/data`中的html文件, 已经隐藏内部细节
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

## 数据库2.0

update 民国114年5月14日19点19分 by devout

新版数据库接口功能基本实现