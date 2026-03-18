---
name: mp-editor
description: WeChat Official Account article editor. Polish articles with LLM, generate AI covers, convert Markdown to WeChat HTML, and publish to WeChat draft box.
trigger: |
  Use when user mentions WeChat Official Account, 公众号, article editing, 润色文章, 生成封面, 发布文章, 排版, 发文, 发公众号.
  Also trigger on commands: /mp setup, /mp help, mp setup, mp help, 初始化, 配置, 设置, 怎么用, 使用帮助.
  Also trigger when user asks: "怎么配置", "怎么安装", "怎么用", "不会用", "怎么获取", "AppID", "AppSecret", "API Key", "IP白名单".
---

# MP-Editor - 公众号 AI 编辑助手

把 Markdown 草稿自动润色、排版、配图，直接发到公众号草稿箱。

## 🚀 新手必读

**第一次使用？** 直接输入：
```
/mp setup
```
AI 会一步步引导你完成配置，不用看下面的文档。

**不知道命令怎么用？** 输入：
```
/mp help
```
查看傻瓜式使用指南。

---

## 配置要求

首次使用需要配置以下信息（运行 `/mp setup` 会有详细引导）：

| 配置项 | 用途 | 获取方式 |
|--------|------|----------|
| `WECHAT_APP_ID` | 微信公众号身份 | [微信公众平台](https://mp.weixin.qq.com/) → 开发 → 基本配置 |
| `WECHAT_APP_SECRET` | 微信公众号密钥 | 同上 |
| `ALIYUN_API_KEY` 或 `GOOGLE_API_KEY` | AI 服务调用 | 阿里云 DashScope 或 Google AI Studio |

配置会自动检测，缺少时会提示你如何获取。

---

## 命令列表

### `/mp setup` - 初始化配置（新手先跑这个）

交互式引导完成所有配置，包括：
- 创建 .env 配置文件
- 检查必填参数
- 测试 API 连通性
- 显示当前 IP（用于微信白名单）
- 跑测试用例验证流程

**示例：**
```
/mp setup
```

---

### `/mp help` - 查看使用帮助

显示完整的傻瓜式使用指南，包括：
- 快速开始步骤
- 所有命令说明
- 常见问题解决

**示例：**
```
/mp help
```

---

### `/mp polish <文件>` - 只润色文章

用 AI 润色文章，生成标题、摘要和优化后的正文，但不发布。

**适合场景：**
- 只想看看 AI 优化后的效果
- 需要手动修改后再发布

**示例：**
```
/mp polish ~/Documents/草稿.md
```

**输出：**
- 标题（20字以内）
- 摘要（50字以内）
- 润色后的 Markdown

---

### `/mp preview <文件>` - 本地预览

生成完整的预览文件，包括 HTML 和封面图，保存在本地查看。

**适合场景：**
- 正式发布前先看效果
- 调整排版样式

**示例：**
```
/mp preview ~/Documents/草稿.md
```

**输出目录**（默认 `./mp-editor-output/`）：
- `article.html` - 公众号格式的 HTML
- `article.md` - 润色后的 Markdown
- `metadata.json` - 文章元数据和封面图 URL

---

### `/mp publish <文件>` - 发布到公众号

完整流程：润色 → 生成封面 → 转 HTML → 上传到公众号草稿箱。

**适合场景：**
- 直接发布，一步到位

**示例：**
```
/mp publish ~/Documents/草稿.md
```

**结果：** 文章出现在公众号后台的草稿箱里，你去后台点群发即可。

---

## 💡 使用流程

```
写草稿 → /mp preview → 满意？→ /mp publish → 去公众号后台群发
            ↓ 不满意
      修改草稿重新来
```

**推荐用法：**
1. 先用 `/mp preview` 看效果
2. 在浏览器打开生成的 article.html 检查
3. 满意后运行 `/mp publish` 正式发布

---

## ⚠️ 常见问题

### 1. 报错 "invalid ip"

**原因：** 微信要求把服务器 IP 加入白名单

**解决：**
1. 运行 `/mp setup` 查看你的 IP 地址
2. 登录 [微信公众平台](https://mp.weixin.qq.com/)
3. 左侧「开发」→「基本配置」→「IP白名单」
4. 添加你的 IP

### 2. 封面图生成失败

**原因：** AI 画图服务暂时不可用

**解决：** 系统会自动切换到备用服务商。如果都失败，会提示你重试。

### 3. 文章发布成功但封面不显示

**原因：** 微信需要把图片上传到自家服务器

**解决：** 这是正常的，系统会自动处理。如果封面没显示，检查 IP 白名单是否配置正确。

### 4. 不知道命令怎么用

运行 `/mp help` 查看完整指南，或直接问 AI：「怎么用 mp-editor？」

Generate local preview without publishing. Creates HTML and downloads cover image.

**Example:**
```
/mp preview ~/Documents/draft.md
```

**Output directory:** `./mp-editor-output/`
- `article.html` - WeChat-formatted HTML
- `article.md` - Polished Markdown
- `metadata.json` - Article metadata and cover image URL

### `/mp publish <file>`

Full pipeline: polish → generate cover → convert to HTML → publish to WeChat draft box.

**Example:**
```
/mp publish ~/Documents/draft.md
```

**Result:** Article appears in WeChat Official Account Platform draft box.

## 🔧 技术说明（给 AI 看的）

### 工作流节点

```
polish → cover_prompt → image_gen → md2html → access_token → upload_material → upload_article
 润色      生成封面提示词    生成封面图     转 HTML     获取微信 token   上传封面素材      发布到草稿箱
```

### AI 服务商

- **文本润色**：默认阿里云 DashScope，失败自动切 Google Gemini
- **封面生成**：默认阿里云 DashScope，失败自动切 Google Gemini

### 配置文件

- `~/.mp-editor/.env` - 用户配置（API 密钥等）
- `config/polish_node_cfg.json` - 润色提示词配置
- `config/cover_prompt_node_cfg.json` - 封面提示词配置
