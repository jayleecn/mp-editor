# MP-Editor · 公众号 AI 编辑助手

> 把写好的 Markdown 草稿丢给 AI，自动润色、排版、配图，直接发到公众号草稿箱。

---

## 🚀 运营同学看这里

**把下面这段话复制给你的 AI 助手，它会帮你装好：**

> 帮我安装 mp-editor 这个 skill，仓库地址是 https://github.com/jayleecn/mp-editor 。安装完成后，指导我配置 env 文件，需要哪些 key 告诉我去哪里找。

装好后，你只需要做两件事：
1. **配置 key**（AI 会指导你）
2. **发稿**（把 Markdown 丢给 AI 就行）

---

## ✨ 能做什么

| 功能 | 说明 |
|------|------|
| **润色文章** | AI 自动优化标题、摘要和正文，保持你的风格 |
| **生成封面** | 根据文章内容自动生成 AI 封面图 |
| **排版转换** | Markdown 自动转成公众号精美的 HTML 格式 |
| **一键发布** | 直接推送到公众号草稿箱，你在后台点一下就能群发 |

---

## 📝 使用方法

装好后，直接给 AI 发指令：

### 1. 本地预览（不发布）
```
/mp preview ~/Documents/我的草稿.md
```
AI 会生成 `article.html` 和封面图，你在浏览器打开看看效果。

### 2. 直接发布到公众号
```
/mp publish ~/Documents/我的草稿.md
```
AI 润色 → 生成封面 → 排版 → 发布到公众号草稿箱。你去公众号后台就能看到。

### 3. 只润色不发布
```
/mp polish ~/Documents/我的草稿.md
```
AI 帮你优化文章，生成新的标题和摘要，输出 Markdown 文件。

---

## 🔧 配置说明

安装完成后，需要配置以下信息（AI 会指导你操作）：

### 1. 微信公众账号（必须）
- `WECHAT_APP_ID` - 公众号 AppID
- `WECHAT_APP_SECRET` - 公众号 AppSecret

**获取方式：**
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 左侧菜单「开发」→「基本配置」
3. 复制 AppID 和 AppSecret

### 2. AI 服务（二选一）

**阿里云 DashScope（推荐，国内稳定）：**
- `ALIYUN_API_KEY` - [阿里云控制台](https://dashscope.console.aliyun.com/) 创建

**Google Gemini（备选）：**
- `GOOGLE_API_KEY` - [Google AI Studio](https://aistudio.google.com/) 创建

配置文件位置：`~/.mp-editor/.env`

---

## ❓ 常见问题

### 发布时报错 "invalid ip"
**原因：** 微信要求把服务器 IP 加入白名单
**解决：** 把报错信息里的 IP 地址，添加到公众号后台「开发」→「基本配置」→「IP 白名单」

### 封面图生成失败
**原因：** AI 画图服务暂时不可用
**解决：** 系统会自动切换到备用服务商，或你可以手动上传封面后使用 `mp 继续发布`

### 找不到配置文件
**原因：** `.env` 文件没创建或位置不对
**解决：** 确保文件在 `~/.mp-editor/.env`，不是 skill 目录下

---

## 🔌 支持的 AI 服务商

| 服务 | 支持情况 |
|------|---------|
| **阿里云 DashScope** | 默认首选，国内访问快 |
| **Google Gemini** | 自动兜底，无需配置也能用 |

系统会自动在多个服务商之间切换，一个挂了自动试另一个。

---

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

---

## 🛠️ 技术架构

```
┌─────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌───────────────┐
│ polish  │ → │ cover_prompt│ → │ image_gen │ → │ md2html │ → │ access_token│ → │ upload_material│ → │ upload_article│
└─────────┘   └─────────────┘   └───────────┘   └─────────┘   └─────────────┘   └────────────────┘   └───────────────┘
   润色文章      生成封面提示词      AI 生成封面      转 HTML      获取微信 token      上传封面素材         发布到草稿箱
```

底层使用 LangGraph 编排工作流，支持多 AI 服务商自动切换。

---

## 📄 License

MIT - 免费用于个人和商业用途。

---

**有问题？** 直接把报错信息发给 AI，它会帮你解决。
