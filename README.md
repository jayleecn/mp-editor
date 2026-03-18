# MP-Editor Skill

A Claude Code skill for editing and publishing WeChat Official Account articles with AI-powered polishing, cover generation, and seamless publishing to WeChat draft box.

## Features

- **Article Polishing**: LLM-powered article refinement with title and abstract generation
- **AI Cover Generation**: Automatic cover image creation based on article content
- **Markdown to HTML**: Converts Markdown to WeChat-optimized HTML with professional styling
- **One-Click Publishing**: Complete workflow from raw text to WeChat draft box
- **Multi-Provider Support**: Supports multiple LLM and image generation providers with automatic fallback

## Supported Providers

### Text LLM Providers (set via `LLM_PROVIDER` env var)

| Provider | Environment Variables | Notes |
|----------|----------------------|-------|
| **Aliyun** (default) | `ALIYUN_API_KEY`, `ALIYUN_MODEL` | DashScope OpenAI-compatible API |
| **Google** | `GOOGLE_API_KEY`, `GOOGLE_MODEL` | Gemini API |

### Image Generation Providers (set via `IMAGE_PROVIDER` env var)

| Provider | Environment Variables | Notes |
|----------|----------------------|-------|
| **Aliyun** (default) | `ALIYUN_API_KEY`, `ALIYUN_IMAGE_MODEL` | DashScope multimodal generation |
| **Google** | `GOOGLE_API_KEY`, `GOOGLE_IMAGE_MODEL` | Gemini image generation |

**Automatic Fallback**: If the primary provider fails, the system automatically tries alternative providers.

## Installation

### 1. Install the Skill

```bash
# Clone or copy to your skills directory
cp -r mp-editor ~/.agents/skills/

# Install dependencies
cd ~/.agents/skills/mp-editor
pip install -r requirements.txt
```

### 2. Configure Environment

Create the configuration directory and copy the example:

```bash
mkdir -p ~/.mp-editor
cp ~/.agents/skills/mp-editor/.env.example ~/.mp-editor/.env
```

Edit `~/.mp-editor/.env` with your API keys:

```bash
# Required: WeChat Official Account
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# Required: LLM Provider (choose at least one)
## For Aliyun (recommended)
ALIYUN_API_KEY=your_aliyun_api_key
ALIYUN_MODEL=qwen3.5-plus
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/

## For Google
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-2.5-flash

# Required: Image Generation (choose at least one)
## For Aliyun (recommended)
ALIYUN_IMAGE_MODEL=z-image-turbo

## For Google
GOOGLE_IMAGE_MODEL=gemini-2.5-flash-image

# Optional: Provider Selection
LLM_PROVIDER=aliyun         # Default: aliyun
IMAGE_PROVIDER=aliyun       # Default: aliyun
```

### 3. Get WeChat Credentials

1. Log in to [WeChat Official Account Platform](https://mp.weixin.qq.com/)
2. Go to "Development" → "Basic Configuration"
3. Copy the AppID and AppSecret

## Usage

### As a Claude Code Skill

Once installed, use these commands in Claude Code:

#### `/mp polish <file>`

Polish an article using LLM. Generates title, abstract, and formatted content.

```
/mp polish ~/Documents/my-article.md
```

**Output:**
- Title (≤20 characters)
- Abstract (≤50 characters, first-person)
- Polished Markdown content

#### `/mp preview <file>`

Generate local preview without publishing. Creates HTML and downloads cover image.

```
/mp preview ~/Documents/my-article.md --output-dir ./preview
```

**Output directory** (default: `./mp-editor-output/`):
- `article.html` - WeChat-formatted HTML
- `article.md` - Polished Markdown
- `metadata.json` - Article metadata and cover image URL

#### `/mp publish <file>`

Full pipeline: polish → generate cover → convert to HTML → publish to WeChat draft box.

```
/mp publish ~/Documents/my-article.md
```

**Result:** Article appears in WeChat Official Account Platform draft box.

### As a CLI Tool

```bash
cd ~/.agents/skills/mp-editor

# Polish only
python -m src.main polish /path/to/article.md

# Generate preview
python -m src.main preview /path/to/article.md --output-dir ./output

# Full publish
python -m src.main publish /path/to/article.md
```

## Workflow

The complete workflow consists of 7 nodes orchestrated by LangGraph:

```
┌─────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌───────────────┐
│ polish  │ → │ cover_prompt│ → │ image_gen │ → │ md2html │ → │ access_token│ → │ upload_material│ → │ upload_article│
└─────────┘   └─────────────┘   └───────────┘   └─────────┘   └─────────────┘   └────────────────┘   └───────────────┘
     │               │                │              │               │                │                   │
  Generate      Generate AI       Generate      Convert       Get WeChat      Upload cover       Publish to
  title/       painting prompt    cover image    to HTML       API token        image            draft box
  abstract
```

1. **polish** - LLM polishes article, generates title/abstract
2. **cover_prompt** - LLM generates AI painting prompt from title/abstract
3. **image_gen** - Generates cover image using AI
4. **md2html** - Converts Markdown to WeChat-friendly HTML
5. **access_token** - Authenticates with WeChat API
6. **upload_material** - Uploads cover image to WeChat
7. **upload_article** - Publishes article to WeChat draft box

## Configuration Files

### Node Configuration

Node behavior can be customized via JSON config files in `config/`:

#### `config/polish_node_cfg.json`

```json
{
    "config": {
        "model": "qwen-max",
        "temperature": 0.8,
        "max_completion_tokens": 4096
    },
    "sp": "System prompt for polishing...",
    "up": "User prompt template with {{content}} variable..."
}
```

#### `config/cover_prompt_node_cfg.json`

```json
{
    "config": {
        "model": "qwen-max",
        "temperature": 0.8
    },
    "sp": "System prompt for cover generation...",
    "up": "User prompt template with {{title}} and {{abstract}} variables..."
}
```

**Configuration Keys:**
- `config`: LLM parameters (model, temperature, etc.)
- `sp`: System prompt
- `up`: User prompt template (Jinja2 format)

## Project Structure

```
mp-editor/
├── SKILL.md                    # Claude Code skill definition
├── README.md                   # This file
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── config/                     # Node configuration files
│   ├── polish_node_cfg.json
│   └── cover_prompt_node_cfg.json
└── src/
    ├── main.py                 # CLI entry point with 3 commands
    ├── llm/                    # LLM and Image services
    │   ├── __init__.py
    │   ├── service.py          # LLMService with fallback
    │   ├── image_service.py    # ImageGenService with fallback
    │   └── providers.py        # Provider implementations
    ├── graphs/                 # LangGraph workflow
    │   ├── __init__.py
    │   ├── graph.py            # Main graph definition
    │   ├── state.py            # Pydantic state models
    │   └── nodes/              # Node implementations
    │       ├── polish_node.py
    │       ├── cover_prompt_node.py
    │       ├── image_gen_node.py
    │       ├── md2html_node.py
    │       ├── access_token_node.py
    │       ├── upload_material_node.py
    │       └── upload_article_node.py
    └── utils/
        └── wechat_client.py    # WeChat API client
```

## Architecture

### Provider Abstraction

The skill uses a provider-agnostic architecture:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   polish    │─────→│  LLMService  │─────→│ AliyunProvider  │
│    node     │      │              │      │ GoogleProvider  │
└─────────────┘      │  (fallback)  │─────→└─────────────────┘
                     └──────────────┘

┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│ image_gen   │─────→│ImageGenService│────→│AliyunImageProvider│
│    node     │      │              │      │GoogleImageProvider│
└─────────────┘      │  (fallback)  │─────→└─────────────────┘
                     └──────────────┘
```

All providers implement a common interface, allowing seamless switching and fallback.

### State Management

Uses Pydantic models for type-safe state flow:

- `GlobalState` - Complete workflow state
- `GraphInput` / `GraphOutput` - Entry/exit boundaries
- Per-node input/output models (e.g., `PolishInput`, `PolishOutput`)

## HTML Styling

The Markdown-to-HTML converter generates WeChat-optimized HTML with:

- **Primary Color**: `#0F4C81` (professional blue)
- **Headings**: Styled with background colors and borders
- **Lists**: Custom bullet points
- **Code Blocks**: Syntax highlighting with Pygments
- **Blockquotes**: Left border accent
- **Links**: WeChat-compatible styling

## Troubleshooting

### "ALIYUN_API_KEY not configured"

Make sure you've created `~/.mp-editor/.env` and set the API keys. The skill loads environment from this location.

### "WeChat configuration missing"

Set `WECHAT_APP_ID` and `WECHAT_APP_SECRET` in your environment file.

### JSON parsing errors

The polish node uses multiple fallback strategies for JSON extraction. If you see parsing warnings, the node will attempt to extract content from markdown or plain text.

### Image generation fails

Check that your image provider API key is valid. The service will automatically fall back to alternative providers if configured.

### Cover image not showing in WeChat

The WeChat material upload downloads the image and re-uploads it to WeChat's servers. Ensure the generated image URL is publicly accessible.

## Requirements

- Python 3.10+
- See `requirements.txt` for package dependencies

## Decoupling from Coze

This skill is a decoupled version of a Coze-native workflow:

- Replaced `coze_coding_dev_sdk.LLMClient` with `LLMService`
- Replaced `coze_coding_dev_sdk.ImageGenerationClient` with `ImageGenService`
- Removed Coze-specific runtime dependencies
- Added environment-based configuration
- Added CLI interface for standalone usage
- Added Claude Code skill integration

## License

MIT License - Free for personal and commercial use.

## Contributing

This skill is designed for the Claude Code/OpenClaw ecosystem. To contribute:

1. Fork the repository
2. Make your changes
3. Test with `python -m src.main preview <file>`
4. Submit a pull request

## Support

For issues or questions:
- Check the troubleshooting section above
- Review logs for detailed error messages
- Ensure all required environment variables are set
