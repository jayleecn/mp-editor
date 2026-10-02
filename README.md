# MP-Editor · 公众号 AI 编辑助手

> 把写好的推文草稿丢给 AI，自动润色、排版、配图，直接发到公众号草稿箱。

***

## 🚀 新媒体运营请看这里

**把下面这段话复制给你的 AI 助手，它会帮你装好：**

> 帮我安装 mp-editor 这个 skill，仓库地址是 <https://github.com/jayleecn/mp-editor> 。安装好后，直接执行 /mp setup 协助我完成初始化设置，并告诉我出口 IP 是多少，方便我添加微信公众号的 IP 白名单

装好后，你只需要做三件事：

1. **配置 key**（AI 会指导你）
2. **添加 IP 白名单**（AI 会指导你）
3. **发稿**（把推文草稿丢给 AI 就行）

***

## ✨ 能做什么

| 功能       | 说明                          |
| -------- | --------------------------- |
| **润色文章** | AI 自动优化标题、摘要和正文，保持你的风格      |
| **生成封面** | 根据文章内容自动生成 AI 封面图           |
| **排版转换** | Markdown 自动转成公众号精美的 HTML 格式 |
| **一键发布** | 直接推送到公众号草稿箱，你在后台点一下就能群发     |

***

## 📝 使用方法

装好后，直接给 AI 发指令：

### 1. 直接发布到公众号（最常用）

```
/mp publish ~/Documents/我的草稿.md
```

AI 润色 → 生成封面 → 排版 → 发布到公众号草稿箱。你去公众号后台就能看到。

### 2. 本地预览（想看效果再用）

```
/mp preview ~/Documents/我的草稿.md
```

AI 会生成 `article.html` 和封面图，你在浏览器打开看看效果。

### 3. 只润色不发布

```
/mp polish ~/Documents/我的草稿.md
```

AI 帮你优化文章，生成新的标题和摘要。CLI 输出包含 `title`、`abstract`、`content` 的 JSON，其中 `content` 是润色后的 Markdown；`-o` 保存的也是该 JSON。

***

## 🔧 配置说明

安装完成后，需要配置以下信息（AI 会指导你操作）：

### 1. 微信公众账号（必须）

- `WECHAT_APP_ID` - 公众号 AppID
- `WECHAT_APP_SECRET` - 公众号 AppSecret

**获取方式：**

1. 登录 [微信开发者平台](https://developers.weixin.qq.com/)
2. 获取你的公众号 APPID 和 AppSecret
3. 访问 [ip38.com](https://ip38.com) 查看你的机器出口 IP
4. 在微信开发者平台添加 IP 白名单

### 2. AI 服务（必须）

**阿里云 DashScope：**

- `ALIYUN_API_KEY` - [阿里云控制台](https://dashscope.console.aliyun.com/) 创建
- `ALIYUN_MODEL`=qwen3.5-plus
- `ALIYUN_IMAGE_MODEL`=z-image-turbo
- `ALIYUN_BASE_URL`=<https://dashscope.aliyuncs.com/compatible-mode/v1/>

配置文件位置：`~/.mp-editor/.env`

***

## ❓ 常见问题

### 发布时报错 "invalid ip"

**原因：** 微信要求把服务器 IP 加入白名单
**解决：**

1. 访问 <https://ip38.com> 查看你的机器出口 IP
2. 到 <https://developers.weixin.qq.com/console/> 登录你的公众号
3. 添加 IP 白名单（填入你从 ip38.com 看到的 IP）

### 封面图生成失败

**原因：** AI 画图服务暂时不可用
**解决：** 请检查阿里云 API Key 是否正确，或稍后重试。

### 找不到配置文件

**原因：** `.env` 文件没创建或位置不对
**解决：** 确保文件在 `~/.mp-editor/.env`，不是 skill 目录下

***

## 🔌 支持的 AI 服务商

| 服务                | 支持情况        |
| ----------------- | ----------- |
| **阿里云 DashScope** | 文本润色 + 封面生成 |

***

## 📁 项目结构（给 AI 看的）

```
mp-editor/
├── SKILL.md                 # Claude Code skill 定义
├── README.md                # 本文件
├── .env.example             # 配置模板
├── requirements.txt         # Python 依赖
├── config/                  # AI 提示词配置
│   ├── polish_node_cfg.json
│   └── cover_prompt_node_cfg.json
└── src/
    ├── main.py              # CLI 入口
    ├── llm/                 # AI 服务封装
    ├── graphs/              # 工作流定义
    └── utils/               # 微信 API 客户端
```

***

## 🛠️ 技术架构

```
┌─────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌───────────────┐
│ polish  │ → │ cover_prompt│ → │ image_gen │ → │ md2html │ → │ access_token│ → │ upload_material│ → │ upload_article│
└─────────┘   └─────────────┘   └─────────┘   └─────────┘   └─────────────┘   └────────────────┘   └───────────────┘
   润色文章      生成封面提示词      AI 生成封面      转 HTML      获取微信 token      上传封面素材         发布到草稿箱
```

底层使用 LangGraph 编排工作流，阿里云 DashScope 提供 AI 服务。

***

## 📄 License

MIT - 免费用于个人和商业用途。

***

**有问题？** 直接把报错信息发给 AI，它会帮你解决。

## 开发与实际执行入口

`/mp …` 是给 AI 助手的任务写法；实际执行的是 Python CLI。它不会仅凭克隆仓库就在终端注册 `/mp` 命令。从仓库根目录安装并查看参数：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.main --help
```

| 助手任务 | 仓库根目录下的实际命令 |
| --- | --- |
| `/mp setup` | `.venv/bin/python -m src.main setup` |
| `/mp help` | `.venv/bin/python -m src.main help` |
| `/mp polish draft.md` | `.venv/bin/python -m src.main polish draft.md` |
| `/mp preview draft.md` | `.venv/bin/python -m src.main preview draft.md` |
| `/mp publish draft.md` | `.venv/bin/python -m src.main publish draft.md` |

`setup` 会创建配置、检查微信/模型连通性并获取出口 IP；`preview` 会调用模型；`publish` 会上传公众号草稿。[scripts/run.sh](scripts/run.sh) 切换到仓库根目录再调用当前 Python；[mp-editor.sh](mp-editor.sh) 是已安装到 `~/.agents/skills/mp-editor` 时的包装器。普通克隆使用上面的 CLI 命令即可。

| 要改的功能 | 入口 |
| --- | --- |
| 参数、配置加载、polish/preview/publish 分派与本地输出 | [src/main.py](src/main.py) |
| 发布工作流和状态模型 | [src/graphs/graph.py](src/graphs/graph.py)、[src/graphs/state.py](src/graphs/state.py) |
| 润色/封面提示词 | [config/polish_node_cfg.json](config/polish_node_cfg.json)、[config/cover_prompt_node_cfg.json](config/cover_prompt_node_cfg.json) |
| HTML 转换与各步骤 | [src/graphs/nodes/md2html_node.py](src/graphs/nodes/md2html_node.py)、[src/graphs/nodes](src/graphs/nodes) |
| 文本/图像模型 | [src/llm/service.py](src/llm/service.py)、[src/llm/providers.py](src/llm/providers.py)、[src/llm/image_service.py](src/llm/image_service.py) |
| 微信 token、素材与草稿 API | [src/utils/wechat_client.py](src/utils/wechat_client.py) |
| AI 助手的命令映射 | [SKILL.md](SKILL.md) |

配置优先读取 `~/.mp-editor/.env`，不存在时读取当前目录 `.env`，否则使用环境变量。模板为 [.env.example](.env.example)。当前只实现 Aliyun 服务；`LLM_PROVIDER` 的其他值会回退到 Aliyun，图像服务固定使用 Aliyun。

离线入口复核用 `.venv/bin/python -m src.main --help` 和 `bash -n scripts/run.sh` 和 `bash -n mp-editor.sh`；实际润色、图片和微信上传需要有效配置。仓库没有自动化测试套件。
