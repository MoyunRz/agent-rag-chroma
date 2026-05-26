# agent-rag-chroma

基于 **Django + Chroma + MiniMax + sentence-transformers** 的中文 RAG 知识库 Demo。

当前项目已经跑通一条最小可用闭环：

- 创建知识库
- 上传或命令行导入文档
- 文档解析与分块
- 本地 embedding 向量化
- Chroma 检索
- MiniMax 生成回答
- 返回引用来源

适合用来快速验证企业知识库问答的基本流程。

## 功能概览

### 已实现

- 知识库创建与列表展示
- 文档入库页面 `/ingestion/`
- RAG 问答页面 `/rag/`
- 健康检查 `/health/`
- 支持文档格式：`TXT`、`Markdown`、`PDF`、`DOCX/DOC`
- 文档版本记录、分块记录、入库失败状态记录
- Chroma 持久化存储
- 基于引用片段的回答生成

### 当前阶段

- M0 架构方案：完成
- M1 Django 工程骨架：完成
- M2 文档入库 MVP：完成
- M3 RAG 问答 MVP：完成
- M4 知识库管理：部分完成
- M5 质量评估：未开始
- M6 部署运维：未开始

## 技术栈

- **Web 框架**：Django 5
- **向量数据库**：Chroma
- **回答生成**：MiniMax Chat API
- **Embedding**：`sentence-transformers`（默认 `BAAI/bge-small-zh-v1.5`）
- **元数据存储**：SQLite（开发环境）
- **文档解析**：`pdfplumber` / `pypdf` / `python-docx`

## 系统流程

```text
文档上传/导入
  -> 解析器读取文本
  -> 分块器按段落切块
  -> 本地 embedding 向量化
  -> 写入 Chroma
  -> 用户提问
  -> 向量检索
  -> Prompt 组装
  -> MiniMax 生成回答
  -> 返回答案 + 引用
```

## 页面入口

| 路径 | 说明 |
| --- | --- |
| `/` | 知识库管理首页 |
| `/ingestion/` | 文档上传与入库 |
| `/rag/` | 知识库问答 |
| `/health/` | 健康检查 |
| `/admin/` | Django Admin |

## 项目结构

```text
agent-rag-chroma/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── middleware.py
│   └── urls.py
├── apps/
│   ├── knowledge/      # 知识库管理
│   ├── ingestion/      # 文档入库、解析、分块
│   └── rag/            # 检索与回答生成
├── integrations/
│   ├── chroma_store.py
│   ├── embedding_client.py
│   └── minimax_client.py
├── templates/
│   ├── knowledge/
│   ├── ingestion/
│   └── rag/
├── docs/
│   ├── 01-architecture.md
│   └── 02-implementation-outline.md
└── data/
    ├── app.db          # SQLite 数据库
    ├── raw/            # 原始上传文档
    └── chroma/         # Chroma 持久化目录
```

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```env
DJANGO_SECRET_KEY=dev-secret-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_BASE_URL=https://api.minimax.chat
MINIMAX_CHAT_MODEL=your_chat_model

EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

CHROMA_MODE=persistent
CHROMA_PERSIST_DIR=./data/chroma
STORAGE_DIR=./data/raw

RAG_DEFAULT_TOP_K=8
RAG_MAX_CONTEXT_CHARS=12000
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=120
```

说明：

- `manage.py` 会自动执行 `load_dotenv()`。
- **文档入库和检索使用本地 embedding 模型**。
- **问答生成依赖 MiniMax Chat API**，因此 `MINIMAX_API_KEY` 和 `MINIMAX_CHAT_MODEL` 需要正确配置。

### 3. 准备本地数据目录

```bash
mkdir -p data/raw data/chroma
```

### 4. 初始化数据库

```bash
python manage.py migrate
```

### 5. 启动服务

```bash
python manage.py runserver
```

启动后访问：

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/ingestion/
- http://127.0.0.1:8000/rag/
- http://127.0.0.1:8000/health/

## 使用方式

### 方式一：Web 页面

1. 打开 `/` 创建一个知识库。
2. 进入 `/ingestion/` 上传文档。
3. 进入 `/rag/` 选择知识库并提问。
4. 查看回答、引用来源、trace 和耗时。

### 方式二：命令行入库

```bash
python manage.py ingest --kb-id 1 --file /absolute/path/to/doc.pdf
```

可选参数：

```bash
python manage.py ingest --kb-id 1 --file /absolute/path/to/doc.pdf --tenant demo
```

## 数据存储说明

默认开发环境下：

- Django 元数据数据库：`data/app.db`
- 原始文档存储目录：`data/raw/`
- Chroma 持久化目录：`data/chroma/`

这些目录已在 `.gitignore` 中忽略，不会提交到仓库。

## 文档解析与分块策略

### 支持的解析器

- `TextParser`：TXT
- `MarkdownParser`：Markdown 标题切分
- `PDFParser`：优先 `pdfplumber`，回退 `pypdf`
- `DocxParser`：Word 段落解析

### 分块策略

当前使用 `SemanticChunker`：

- 按段落切分
- 超过 `RAG_CHUNK_SIZE` 时切块
- 保留 `RAG_CHUNK_OVERLAP` 重叠字符
- 为每个 chunk 记录页码、标题路径、hash、chroma_id

## 生产配置

项目已预留生产配置：

- `config.settings.prod`
- `DEBUG=False`
- PostgreSQL 作为元数据数据库
- 需要额外安装 PostgreSQL 驱动（如 `psycopg`）

示例：

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py runserver
```

生产环境还需要补充：

- PostgreSQL 实例
- 反向代理与静态文件处理
- 容器化部署
- 监控与日志采集

## 注意事项

- 当前是 **Demo 项目**，尚未实现认证、RBAC、ACL 等企业级权限隔离。
- 首次使用本地 embedding 模型时，`sentence-transformers` 可能会下载模型文件。
- RAG 回答要求依赖已入库文档；如果知识库为空或检索不到内容，会返回“当前知识库中未找到足够依据来回答这个问题”。

## 常见问题

### 1. MiniMax 认证失败

通常检查：

- `MINIMAX_API_KEY` 是否正确
- `.env` 是否被正确加载
- `MINIMAX_CHAT_MODEL` 是否已配置

### 2. MiniMax 返回余额不足

如果接口返回余额不足相关错误，需要先为 MiniMax 账户充值后再测试问答。

### 3. Chroma 无法读取

检查：

- `CHROMA_PERSIST_DIR` 是否可写
- `data/chroma/` 是否存在权限问题
- `/health/` 返回的 `chroma` 字段内容

## 后续计划

- 完善知识库管理能力
- 增加文档删除 / 重建索引
- 增加质量评估与反馈闭环
- 增加 Docker Compose 部署方案
- 增加生产环境运行手册

## 参考文档

- `docs/01-architecture.md`
- `docs/02-implementation-outline.md`
