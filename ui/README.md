# 选课辅助系统前端

## 项目介绍（AI生成的）
这是选课辅助系统的前端界面，使用 Vue 3 + Element Plus 构建。该界面提供了课程管理、培养方案导入、大模型配置等功能。

## 目录结构
```
选课辅助系统/
├── ui/                # 前端项目目录
│   ├── src/          # 源代码
│   ├── public/       # 静态资源
│   └── package.json  # 项目配置
├── ...               # 其他目录
└── README.md         # 项目说明
```

## 环境要求
- Node.js 16.0 或更高版本
- pnpm 包管理器

## 安装步骤

1. 安装 Node.js
   - 访问 [Node.js 官网](https://nodejs.org/) 下载并安装
   - 建议安装 LTS（长期支持）版本

2. 安装 pnpm
   ```bash
   npm install -g pnpm
   ```

3. 进入前端项目目录
   ```bash
   cd ui
   ```

4. 安装项目依赖
   ```bash
   pnpm install
   ```

## 开发环境运行
需要先进入 `ui` 目录，下同。
```bash
pnpm run dev
```

## 生产环境构建
```bash
pnpm run build
```

## 预览生产环境构建
```bash
pnpm preview
```

## 主要依赖
- Vue 3
- Element Plus
- Vite


## 常见问题
1. 如果安装依赖时遇到问题
   - 确保已进入 ui 目录
   - 尝试清除 pnpm 缓存：`pnpm store prune`
   - 重新安装：`pnpm install`

2. 如果运行时报错
   - 检查是否在 ui 目录下执行命令
   - 检查 Node.js 版本是否符合要求
   - 确保所有依赖都已正确安装