# BBC News Translator

## 项目简介

BBC News Translator 是一个功能完整的新闻处理系统，能够自动获取 BBC 新闻，翻译成中文，并使用 AI 进行润色，最终提供一个现代化的前端界面供用户浏览和管理。

## 核心功能

### 1. 新闻爬取
- 自动获取 BBC News 网站 "Most Read" 部分的新闻
- 提取新闻标题、链接和发布时间
- 支持增量爬取，避免重复数据

### 2. 内容获取
- 自动访问新闻详情页，提取完整文章内容
- 处理动态加载的内容，确保获取完整文本

### 3. 翻译功能
- 使用 AI 模型将英文新闻翻译成中文
- 保持翻译质量和准确性
- 自动保存翻译结果到数据库

### 4. AI 润色
- 使用 AI 对翻译后的中文内容进行润色
- 提升中文表达质量和流畅度
- 保留原文意思的同时优化语言表达

### 5. 前端界面
- 现代化的 Vue 3 前端应用
- 新闻列表展示，支持关键词搜索
- 按状态筛选（已爬取、已翻译、已润色）
- 文章详情页，英文、中文、AI 润色三栏对比
- 支持复制内容到剪贴板
- 响应式设计，适配移动端和桌面端

### 6. 数据管理
- SQLite 数据库存储
- 完整的 CRUD 操作
- 支持按标题搜索新闻

## 技术栈

### 后端
- **Python 3.10+**
- **Flask** - RESTful API 框架
- **SQLite** - 轻量级数据库
- **Playwright** - 浏览器自动化（用于爬取动态内容）
- **AI 模型** - 用于翻译和润色

### 前端
- **Vue 3** - 前端框架
- **Vue Router** - 路由管理
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 项目结构

```
news/
├── backend/                 # 后端代码
│   ├── src/                 # 源代码
│   │   ├── api.py           # Flask API 入口
│   │   ├── crawler/         # 爬虫模块
│   │   ├── ai/              # AI 模型调用
│   │   └── models/          # 数据库模型
│   ├── config/              # 配置文件
│   │   └── config.py        # 主配置文件
│   ├── db/                  # 数据库目录
│   │   └── news.db          # SQLite 数据库文件
│   ├── logs/                # 日志目录
│   ├── venv/                # Python 虚拟环境
│   └── requirements.txt     # Python 依赖
├── frontend/                # 前端代码
│   ├── src/                 # 源代码
│   │   ├── views/           # 页面组件
│   │   │   ├── Home.vue     # 新闻列表页
│   │   │   └── Article.vue  # 文章详情页
│   │   ├── api.js           # API 调用封装
│   │   ├── router/          # 路由配置
│   │   └── main.js          # 前端入口
│   ├── public/              # 静态资源
│   ├── index.html           # HTML 模板
│   ├── package.json         # 前端依赖
│   └── vite.config.js       # Vite 配置
└── README.md                # 项目说明文档
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <项目地址>
cd news
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境
cd backend
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
export PLAYWRIGHT_BROWSERS_PATH=0
playwright install
```

### 3. 安装前端依赖

```bash
# 回到项目根目录
cd ../frontend

# 安装依赖
npm install
```

## 配置说明

### 1. 数据库配置

数据库配置位于 `backend/config/config.py` 文件中：

```python
# 数据库配置
DATABASE_CONFIG = {
    "path": BASE_DIR / "db" / "news.db"
}
```

### 2. AI 模型配置

AI 模型的 API 密钥需要配置在环境变量中：

```bash
# 在 backend 目录下创建 .env 文件
touch .env

# 编辑 .env 文件，添加 API 密钥
# 示例：
# QWEN_API_KEY=your_api_key_here
```

### 3. 前端 API 代理配置

前端 API 代理配置位于 `frontend/vite.config.js` 文件中：

```javascript
// 示例配置
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5001',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 启动步骤

### 1. 启动后端服务

```bash
# 激活虚拟环境（如果未激活）
cd backend
source venv/bin/activate

# 启动 Flask 服务
python src/api.py

# 服务将在 http://127.0.0.1:5001 运行
```

### 2. 启动前端服务

```bash
# 打开新终端
cd frontend

# 启动 Vue 开发服务器
npm run dev

# 服务将在 http://localhost:3000 运行
```

## 使用指南

### 1. 获取新闻

1. 访问前端界面：http://localhost:3000
2. 点击 "获取最新新闻" 按钮
3. 系统将自动爬取 BBC News 的 "Most Read" 新闻
4. 新闻将显示在列表中

### 2. 翻译新闻

1. 在新闻列表中，找到状态为 "已爬取" 的新闻
2. 点击 "获取原文并翻译" 按钮
3. 系统将自动获取文章内容并翻译成中文
4. 翻译完成后，新闻状态将变为 "已翻译"

### 3. AI 润色

1. 在新闻列表中，点击已翻译的新闻标题，进入详情页
2. 在 "AI 润色" 面板中，点击 "AI 润色" 按钮
3. 系统将使用 AI 对中文内容进行润色
4. 润色完成后，新闻状态将变为 "已润色"

### 4. 搜索和筛选

1. 在搜索框中输入关键词，按回车键或点击 "搜索" 按钮
2. 系统将显示标题包含关键词的新闻
3. 使用状态筛选下拉菜单，可以按状态筛选新闻

## 常见问题

### 1. 爬取失败

- **原因**：网络连接问题或 BBC 网站结构变化
- **解决方法**：检查网络连接，或更新爬虫代码以适应网站结构变化

### 2. 翻译失败

- **原因**：AI 模型 API 密钥配置错误或网络问题
- **解决方法**：检查 .env 文件中的 API 密钥配置，确保网络连接正常

### 3. 前端无法连接后端

- **原因**：后端服务未启动或端口配置错误
- **解决方法**：确保后端服务已启动，检查 vite.config.js 中的代理配置

### 4. 数据库连接失败

- **原因**：数据库文件权限问题或路径错误
- **解决方法**：检查 db 目录权限，确保 config.py 中的数据库路径正确

## 项目状态

- ✅ 核心功能已实现
- ✅ 前端界面已完成
- ✅ 后端 API 已完善
- ✅ 数据库结构已优化
- ✅ 部署配置已就绪

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

如有问题或建议，请联系项目维护者。