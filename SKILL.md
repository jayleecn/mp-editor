---
name: mp-editor
description: WeChat Official Account article editor. Polish articles with LLM, generate AI covers, convert Markdown to WeChat HTML, and publish to WeChat draft box.
trigger: Use when user wants to polish WeChat articles, generate cover images, convert Markdown to WeChat HTML, or publish to WeChat Official Account. Triggers include "polish article", "generate cover", "wechat publish", "mp publish", "公众号", "润色文章", "生成封面".
---

# MP-Editor - WeChat Article Editor

A complete workflow for editing and publishing WeChat Official Account articles with AI-powered polishing and cover generation.

## Prerequisites

Before first use, install dependencies:

```bash
cd ~/.agents/skills/mp-editor
pip install -r requirements.txt
```

Configure environment:

```bash
mkdir -p ~/.mp-editor
cp ~/.agents/skills/mp-editor/.env.example ~/.mp-editor/.env
# Edit ~/.mp-editor/.env with your API keys
```

Required for LLM:
- `LLM_PROVIDER` (aliyun|google)
- Corresponding API keys (`ALIYUN_API_KEY` or `GOOGLE_API_KEY`)

Required for image generation:
- `IMAGE_PROVIDER` (aliyun|google)
- Corresponding API keys

Required for WeChat publishing:
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`

## Commands

### `/mp polish <file>`

Polish an article using LLM. Generates title, abstract, and formatted content.

**Example:**
```
/mp polish ~/Documents/draft.md
```

**Output:**
- Title (≤20 chars)
- Abstract (≤50 chars, first person)
- Polished Markdown content

### `/mp preview <file>`

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

## Workflow

The complete workflow consists of 7 nodes:

1. **polish** - LLM polishes article, generates title/abstract
2. **cover_prompt** - LLM generates AI painting prompt from title/abstract
3. **image_gen** - Generates cover image using AI
4. **md2html** - Converts Markdown to WeChat-friendly HTML
5. **access_token** - Authenticates with WeChat API
6. **upload_material** - Uploads cover image to WeChat
7. **upload_article** - Publishes article to WeChat draft box

## LLM Providers

Text LLM (set `LLM_PROVIDER`):
- **aliyun** - Aliyun DashScope (OpenAI-compatible)
- **google** - Google Gemini

Image Generation (set `IMAGE_PROVIDER`):
- **aliyun** - Aliyun DashScope Image Generation
- **google** - Google Gemini Image Generation

Automatic fallback is enabled between providers.

## Configuration Files

- `config/polish_node_cfg.json` - Polishing prompts and model config
- `config/cover_prompt_node_cfg.json` - Cover prompt generation config

## Technical Notes

- Built with LangGraph for workflow orchestration
- Provider-agnostic LLM and Image services
- Supports multiple LLM backends with automatic fallback
- Decoupled from Coze SDK for standalone use
