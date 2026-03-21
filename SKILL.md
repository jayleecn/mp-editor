---
name: mp-editor
description: WeChat Official Account article editor. Polish articles with LLM, generate AI covers, convert Markdown to WeChat HTML, and publish to WeChat draft box.
trigger: |
  Use when user mentions WeChat Official Account, 公众号, article editing, 润色文章, 生成封面, 发布文章, 发稿, 排版, 发文, 发公众号.
  Also trigger on commands: /mp setup, /mp help, mp setup, mp help, 初始化, 配置, 设置, 怎么用, 使用帮助.
  Also trigger when user asks: "怎么配置", "怎么安装", "怎么用", "不会用", "怎么获取", "AppID", "AppSecret", "API Key", "IP白名单".
allowed-tools: []
disable: false
---

# MP-Editor - 公众号 AI 编辑助手

把推文草稿自动润色、排版、配图，直接发到公众号草稿箱。

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

***

## 配置要求

首次使用需要配置以下信息（运行 `/mp setup` 会有详细引导）：

| 配置项                 | 用途      | 获取方式                                                         |
| ------------------- | ------- | ------------------------------------------------------------ |
| `WECHAT_APP_ID`     | 微信公众号身份 | [微信开发者平台](https://developers.weixin.qq.com/) → 获取你的公众号 APPID |
| `WECHAT_APP_SECRET` | 微信公众号密钥 | 同上                                                           |
| `ALIYUN_API_KEY`    | AI 服务调用 | [阿里云 DashScope](https://dashscope.console.aliyun.com/)       |

**配置步骤：**

1. 到 <https://developers.weixin.qq.com/console/>获取你的公众号 APPID 和 AppSecret
2. 访问 <https://ip38.com> 查看你的机器出口 IP
3. 在微信开发者平台添加 IP 白名单

配置会自动检测，缺少时会提示你如何获取。

***

## 命令列表

### `/mp setup` - 初始化配置（新手先跑这个）

交互式引导完成所有配置，包括：

- 创建 .env 配置文件（若还没有）
- 检查必填参数
- 测试 API 连通性
- 显示当前 IP（用于微信白名单）
- 跑测试用例验证流程

**示例：**

```
/mp setup
```

***

### `/mp help` - 查看使用帮助

显示完整的傻瓜式使用指南，包括：

- 快速开始步骤
- 所有命令说明
- 常见问题解决

**示例：**

```
/mp help
```

***

### `/mp publish <文件>` - 发布到公众号（最常用）

完整流程：润色 → 生成封面 → 转 HTML → 上传到公众号草稿箱。

**适合场景：**

- 直接发布，一步到位
- 这是你最常用的命令

**示例：**

```
/mp publish ~/Documents/草稿.md
```

**结果：** 文章出现在公众号后台的草稿箱里，你去后台点群发即可。

***

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

***

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

***

## 💡 使用流程

```
写草稿 → /mp publish → 去公众号后台群发
            ↓ 想先看效果
      /mp preview → 满意？→ /mp publish
```

**推荐用法：**

1. 直接用 `/mp publish` 发布（最省事）
2. 想先检查效果？用 `/mp preview` 生成本地预览
3. 在浏览器打开 `article.html` 检查
4. 满意后运行 `/mp publish` 正式发布

***

## ⚠️ 常见问题

### 1. 报错 "invalid ip"

**原因：** 微信要求把服务器 IP 加入白名单

**解决：**

1. 访问 <https://ip38.com> 查看你的机器出口 IP
2. 到 <https://developers.weixin.qq.com/> 登录你的公众号
3. 添加 IP 白名单（填入你从 ip38.com 看到的 IP）

### 2. 封面图生成失败

**原因：** AI 画图服务暂时不可用

**解决：** 请检查阿里云 API Key 是否正确，或稍后重试。

### 3. 不知道命令怎么用

运行 `/mp help` 查看完整指南，或直接问 AI：「怎么用 mp-editor？」

***

## 🔧 技术说明（给 AI 看的）

### 工作流节点

```
polish → cover_prompt → image_gen → md2html → access_token → upload_material → upload_article
 润色      生成封面提示词    生成封面图     转 HTML     获取微信 token   上传封面素材      发布到草稿箱
```

### AI 服务商

- **文本润色**：阿里云 DashScope
- **封面生成**：阿里云 DashScope

### 配置文件

- `~/.mp-editor/.env` - 用户配置（API 密钥等）
- `config/polish_node_cfg.json` - 润色提示词配置
- `config/cover_prompt_node_cfg.json` - 封面提示词配置
