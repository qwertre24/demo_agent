# Demo Agent

基于 **LlamaIndex FunctionAgent + Ollama + SQLite** 的本地私人助手示例。

项目当前实现了一个可调用的本地 Agent，并通过工具让模型完成基础计算、受限文件读取、文件写入和历史记忆读取。项目重点不是追求复杂功能，而是逐步实践工具调用、异常处理、路径安全和资源边界。

## 当前功能

- 使用 LlamaIndex `FunctionAgent` 构建工具调用工作流。
- 使用 Ollama 在本地运行大语言模型。
- 使用 SQLite 保存对话历史。
- 提供计算器工具，支持：
  - `add` / `+`
  - `sub` / `-`
  - `mul` / `*`
  - `div` / `/`
  - `pow` / `^`
- 提供受限文本文件读取工具。
- 提供基础文件写入工具。
- 提供按角色和会话隔离的历史记忆读取工具。
- `read_memory` 只返回 `user/system` 记忆，并带有明确的成功返回头。
- 计算器已处理非法运算符和除零异常。
- `read_file` 已处理路径越界、符号链接、文件类型和文件大小限制。
- 数据库初始化已处理提交、回滚和连接关闭。

## 系统结构

```text
用户
  |
  v
命令行交互 demo_agent.py
  |
  v
LlamaIndex FunctionAgent
  |
  +-- calculator
  +-- read_file
  +-- write_file
  +-- read_memory
  |
  +-- Ollama 本地模型
  |
  +-- SQLite 历史记忆
```

## 项目结构

```text
Langchain/
├── code/
│   ├── data/                    # read_file 允许读取的根目录（本地运行时创建）
│   ├── storage/                 # SQLite 等内部状态（本地运行时创建）
│   ├── tools/
│   │   ├── calculator.py
│   │   ├── read_file.py
│   │   └── write_file.py
│   ├── config.py                # 路径、文件大小和扩展名配置
│   └── demo_agent.py            # Agent 和命令行入口
├── notes/                       # 学习笔记与课程资料
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

`.env`、`code/data/`、`code/storage/`、数据库、缓存和 IDE 配置不会提交到 Git。

## 技术栈

- Python 3.14+
- LlamaIndex Core
- LlamaIndex Ollama Integration
- Ollama
- SQLite
- pathlib
- asyncio

## 环境要求

- 已安装 Python 3.14 或更高版本。
- 已安装 Ollama。
- 本机可以运行当前配置的模型。
- 建议至少准备足够运行模型的显存或内存。

当前 `demo_agent.py` 配置的模型是：

```text
qwen2.5:3b
```

首次使用前拉取模型：

```powershell
ollama pull qwen2.5:3b
ollama run qwen2.5:3b "只回复：测试成功"
```

## 安装依赖

当前 `pyproject.toml` 还没有完整声明运行时依赖。建议先补充：

```powershell
uv add llama-index-core llama-index-llms-ollama
uv sync
```

如果使用现有虚拟环境，也可以直接通过 pip 安装对应依赖。

> 注意：仅执行当前的 `uv sync` 不足以安装本项目实际需要的 LlamaIndex 和 Ollama 集成包，因为这些依赖尚未写入 `pyproject.toml`。

## 初始化本地目录

项目的读取目录和存储目录被 Git 忽略，因此首次运行时需要手动创建：

```powershell
New-Item -ItemType Directory -Force code\data
New-Item -ItemType Directory -Force code\storage
```

可以创建测试文件：

```text
code/data/test.txt
code/data/report.md
code/data/child/child.txt
```

SQLite 数据库会在初始化时自动创建：

```text
code/storage/memorise.db
```

SQLite 不会自动创建缺失的父目录，因此 `code/storage` 必须存在。

## 运行项目

从项目根目录运行：

```powershell
uv run python code/demo_agent.py
```

或者使用现有虚拟环境：

```powershell
.\.venv\Scripts\python.exe code\demo_agent.py
```

启动后会进入交互循环：

```text
User>>
```

输入 `exit` 退出。

## 使用示例

### 计算

```text
计算 12 加 8，使用 calculator 工具。
```

### 读取文件

```text
读取 test.txt 的内容。
```

`read_file` 只允许访问 `code/data/`，支持：

- `.txt`
- `.md`
- `.json`

单次最大读取大小为 1 MB。

### 写入文件

当前 `write_file` 是基础版本，可以写文本文件，但还没有实现安全根目录限制。不要在包含敏感文件的目录中暴露该工具。

### 读取记忆

```text
调用 read_memory，告诉我当前保存了多少条历史记录。
```

### 保存记忆

每轮用户输入和 Agent 回复都会写入 SQLite 表：

```text
memorise
```

表结构目前为：

```text
id
session_id
role
content
create_time
```

## 安全边界

### `read_file`

已实现以下约束：

- 只允许相对路径。
- 最终路径必须位于 `code/data/` 内。
- 拒绝通过 `..` 跳出读取根目录。
- 默认拒绝符号链接。
- 拒绝目录和非普通文件。
- 只允许 `.txt`、`.md`、`.json`。
- 默认最大读取 1 MB。
- 强制使用 UTF-8 严格解码。
- 路径越界抛出 `PermissionError`。
- 参数格式错误抛出 `ValueError`。
- 文件系统错误保留原始异常类型。

### `write_file`

当前尚未实现与 `read_file` 对等的安全边界：

- 没有允许写入根目录。
- 没有路径穿越保护。
- 没有符号链接保护。
- 没有原子写入。
- 没有大小限制。
- 没有覆盖保护。

该模块是后续需要优先修复的安全风险。

## 当前进度

### 已完成

- 基础 Agent 和命令行循环。
- Ollama 模型接入。
- 计算器工具及异常处理。
- SQLite 初始化、提交、回滚和连接关闭。
- SQLite 对话历史保存。
- `read_file` 路径边界和文件读取校验。
- 记忆表增加 `session_id` 和 `role` 字段。
- 旧记录迁移为 `legacy`，不再返回给模型。
- `read_memory` 只读取 `user/system` 记忆，并限制为最近 20 条。
- 工具返回明确的“成功读取到长期记忆”头部。
- 初始化失败时以非零状态退出。
- Git 分支整理和敏感文件忽略规则。

### 进行中

- 增加结构化事实提取和长期记忆摘要。
- 统一工具的参数类型、返回类型和 Docstring。
- 为 `write_file` 增加安全边界。

### 待完成

- 将 `write_file` 改为安全、原子、受限目录写入。
- 补齐 `pyproject.toml` 运行时依赖。
- 为工具模块增加单元测试。
- 增加日志系统，替代直接使用 `print`。
- 将模型名、上下文窗口和超时参数移动到配置模块。

## 已知限制

- `legacy` 旧记录不会再返回；如果旧数据包含需要保留的用户事实，需要单独迁移。
- 助手消息会保存用于审计，但 `read_memory` 不会返回，尚未实现长期事实提取。
- `write_file` 目前允许模型写入任意路径，存在严重安全风险。
- 小型本地模型仍可能错误解释其他工具的结果，需要持续加强工具返回契约。
- 项目还没有自动化测试。
- `pyproject.toml` 尚未覆盖实际运行依赖。
- `main.py` 目前不是实际应用入口，正式入口是 `code/demo_agent.py`。

## 后续路线

1. 完成 `write_file` 的路径边界和异常处理。
2. 增加 `facts` 表和记忆摘要，区分消息历史与长期事实。
3. 实现多会话 `session_id` 管理和记忆摘要策略。
4. 补齐依赖声明和锁文件。
5. 增加 `pytest` 测试：
   - 计算器正常和异常路径。
   - 文件读取路径越界。
   - 符号链接拒绝。
   - 数据库初始化和写入回滚。
6. 增加结构化日志、配置加载和启动检查。
7. 评估是否接入 FastAPI 或 Web UI。

## 开发检查

语法检查：

```powershell
python -m py_compile code\demo_agent.py code\config.py code\tools\*.py
```

运行测试文件时要注意：

- `read_file` 的测试文件必须放在 `code/data/`。
- SQLite 测试不应直接修改真实记忆数据库，建议使用临时数据库。
- 不要提交 `.env`、数据库和用户文档。

## License

本项目使用仓库中的 [LICENSE](LICENSE) 文件所列许可证。
