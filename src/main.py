#!/usr/bin/env python3
"""
MP-Editor Skill - Main entry point

WeChat Official Account article editor with LLM-powered polishing,
cover generation, and publishing to WeChat draft box.
"""
import os
import sys
import json
import argparse
import logging
import socket
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Add src to path (main.py is inside src/)
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from graphs import main_graph, GraphInput

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Help message in Chinese
HELP_MESSAGE = """
╔══════════════════════════════════════════════════════════════╗
║              MP-Editor · 公众号 AI 编辑助手                    ║
╚══════════════════════════════════════════════════════════════╝

📖 快速开始
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第一次使用？请先运行初始化：

    /mp setup

AI 会一步步引导你完成配置，不用看文档也能搞定。

📋 常用命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  /mp setup              → 初始化配置（新手必跑）
2️⃣  /mp help               → 显示本帮助
3️⃣  /mp polish <文件>       → 只润色文章，不发布
4️⃣  /mp preview <文件>      → 本地预览效果
5️⃣  /mp publish <文件>      → 发布到公众号草稿箱

💡 使用示例
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 准备你的文章草稿（Markdown 格式）：

    # 我的标题

    这是文章正文...

2. 保存为文件，比如 ~/Desktop/草稿.md

3. 让 AI 帮你处理：

    /mp preview ~/Desktop/草稿.md    # 先看效果
    /mp publish ~/Desktop/草稿.md    # 直接发布

⚠️  注意事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 发布前需要配置微信公众号参数（AppID/AppSecret）
• 需要配置 AI 服务密钥（阿里云或 Google）
• 如果报错 "invalid ip"，需要把 IP 加到微信白名单
• 运行 /mp setup 可以检查配置并获取详细帮助

❓ 遇到问题？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

直接告诉 AI 你遇到了什么错误，它会帮你解决。
或者运行 /mp setup 重新检查配置。

"""


def load_env():
    """Load environment variables from ~/.mp-editor/.env or .env file."""
    # Try loading from ~/.mp-editor/.env first
    home_env = Path.home() / ".mp-editor" / ".env"
    if home_env.exists():
        load_dotenv(home_env)
        logger.info(f"Loaded environment from {home_env}")
        return

    # Try loading from current directory .env
    if Path(".env").exists():
        load_dotenv(".env")
        logger.info("Loaded environment from .env")
        return

    logger.warning("No .env file found. Using environment variables.")


def check_config() -> Tuple[bool, List[Dict]]:
    """
    Check if all required configuration is present.
    Returns: (is_valid, list_of_issues)
    """
    issues = []

    # Check WeChat config
    wechat_app_id = os.getenv("WECHAT_APP_ID")
    wechat_secret = os.getenv("WECHAT_APP_SECRET")

    if not wechat_app_id or wechat_app_id == "your_wechat_app_id":
        issues.append({
            "type": "error",
            "name": "WECHAT_APP_ID",
            "message": "微信公众号 AppID 未配置",
            "guide": """
📱 如何获取 WECHAT_APP_ID：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 登录微信公众平台：https://mp.weixin.qq.com/
2. 左侧菜单找到「开发」→「基本配置」
3. 页面顶部可以看到「开发者ID」，复制「AppID」
4. 粘贴到 ~/.mp-editor/.env 文件中

💡 示例：
WECHAT_APP_ID=wx1234567890abcdef
"""
        })

    if not wechat_secret or wechat_secret == "your_wechat_app_secret":
        issues.append({
            "type": "error",
            "name": "WECHAT_APP_SECRET",
            "message": "微信公众号 AppSecret 未配置",
            "guide": """
🔑 如何获取 WECHAT_APP_SECRET：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 在同一个页面（开发 → 基本配置）
2. 找到「开发者密码(AppSecret)」
3. 点击「重置」或「查看」（需要管理员扫码）
4. 复制 AppSecret
5. 粘贴到 ~/.mp-editor/.env 文件中

⚠️  重要：AppSecret 只显示一次，请妥善保存！
"""
        })

    # Check LLM config
    llm_provider = os.getenv("LLM_PROVIDER", "aliyun")
    aliyun_key = os.getenv("ALIYUN_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    has_aliyun = aliyun_key and aliyun_key != "your_aliyun_api_key_here"
    has_google = google_key and google_key != "your_google_api_key_here"

    if not has_aliyun and not has_google:
        issues.append({
            "type": "error",
            "name": "AI_API_KEY",
            "message": "未配置任何 AI 服务密钥",
            "guide": """
🤖 如何获取 AI 服务密钥（二选一）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

方案 A：阿里云 DashScope（推荐，国内稳定）
────────────────────────────────────────────────────────────
1. 访问：https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 进入「API-KEY 管理」
4. 点击「创建新的 API-KEY」
5. 复制 key 到 ~/.mp-editor/.env：
   ALIYUN_API_KEY=your_key_here

方案 B：Google Gemini（备选）
────────────────────────────────────────────────────────────
1. 访问：https://aistudio.google.com/
2. 登录 Google 账号
3. 点击「Get API key」
4. 创建新的 API key
5. 复制 key 到 ~/.mp-editor/.env：
   GOOGLE_API_KEY=your_key_here
   LLM_PROVIDER=google

💡 建议：先配置阿里云，国内访问更快更稳定
"""
        })

    return len(issues) == 0, issues


def get_public_ip() -> str:
    """Get the public IP address."""
    try:
        import urllib.request
        with urllib.request.urlopen('https://api.ipify.org', timeout=5) as response:
            return response.read().decode('utf-8')
    except Exception:
        return "无法获取（请访问 https://ip.sb 查看）"


def create_env_template():
    """Create .env file from template."""
    env_dir = Path.home() / ".mp-editor"
    env_file = env_dir / ".env"
    template_file = Path(__file__).parent.parent / ".env.example"

    if env_file.exists():
        return False, f"配置文件已存在：{env_file}"

    env_dir.mkdir(parents=True, exist_ok=True)

    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        # Default template if example not found
        template = """# 微信公众号配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# Aliyun LLM
ALIYUN_API_KEY=your_aliyun_api_key_here
ALIYUN_MODEL=qwen3.5-plus
ALIYUN_IMAGE_MODEL=z-image-turbo
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/

# Google LLM
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.5-flash
GOOGLE_IMAGE_MODEL=gemini-2.5-flash-image
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Text LLM Provider
LLM_PROVIDER=aliyun

# Image Generation Provider
IMAGE_PROVIDER=aliyun
"""

    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(template)

    return True, f"配置文件已创建：{env_file}"


def test_llm_connection() -> Tuple[bool, str]:
    """Test LLM connection."""
    try:
        from llm.service import LLMService
        from llm.providers import Message

        service = LLMService()
        messages = [Message(role="user", content="Hello")]
        result = service.chat_sync_with_fallback_config(messages, {})
        return True, "LLM 连接正常"
    except Exception as e:
        return False, f"LLM 连接失败：{str(e)}"


def test_wechat_connection() -> Tuple[bool, str]:
    """Test WeChat API connection."""
    try:
        from utils.wechat_client import WeChatClient

        app_id = os.getenv("WECHAT_APP_ID")
        app_secret = os.getenv("WECHAT_APP_SECRET")

        if not app_id or not app_secret:
            return False, "微信配置不完整"

        client = WeChatClient(app_id, app_secret)
        token = client.get_access_token()
        return True, "微信 API 连接正常" if token else "微信 API 连接失败"
    except Exception as e:
        return False, f"微信 API 连接失败：{str(e)}"


def cmd_setup(args):
    """Setup command: interactive configuration guide."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              MP-Editor · 初始化配置向导                        ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Step 1: Check if .env exists
    env_file = Path.home() / ".mp-editor" / ".env"

    if not env_file.exists():
        print("📁 步骤 1/5：创建配置文件")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        success, msg = create_env_template()
        print(msg)
        print(f"\n✅ 已创建配置文件模板")
        print(f"📍 位置：{env_file}")
        print("\n⏳ 请编辑这个文件，填入你的 API 密钥...")
    else:
        print("📁 步骤 1/5：配置文件已存在")
        print(f"📍 位置：{env_file}")
        load_env()

    # Step 2: Check configuration
    print("\n\n🔍 步骤 2/5：检查配置")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    is_valid, issues = check_config()

    if not is_valid:
        print(f"\n⚠️  发现 {len(issues)} 个配置问题：\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue['message']}")
            print(issue['guide'])
            print()

        print("=" * 60)
        print("❌ 配置检查未通过")
        print("\n💡 解决方法：")
        print(f"   编辑配置文件：{env_file}")
        print("   填入上述缺少的参数后，重新运行 /mp setup")
        return
    else:
        print("\n✅ 所有必填配置项已填写")

    # Step 3: Test connections
    print("\n\n🧪 步骤 3/5：测试 API 连接")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    llm_ok, llm_msg = test_llm_connection()
    wechat_ok, wechat_msg = test_wechat_connection()

    if llm_ok:
        print(f"  ✅ {llm_msg}")
    else:
        print(f"  ❌ {llm_msg}")

    if wechat_ok:
        print(f"  ✅ {wechat_msg}")
    else:
        print(f"  ❌ {wechat_msg}")

    # Step 4: Show IP for whitelist
    print("\n\n🌐 步骤 4/5：IP 白名单配置")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    ip = get_public_ip()
    print(f"\n📍 你的出口 IP 地址：{ip}")
    print("""
⚠️  发布前请确保把这个 IP 添加到微信白名单：

1. 登录微信公众平台：https://mp.weixin.qq.com/
2. 左侧菜单「开发」→「基本配置」
3. 找到「IP白名单」，点击「查看」
4. 添加你的 IP 地址
""")

    # Step 5: Run test
    if llm_ok and wechat_ok:
        print("\n\n🚀 步骤 5/5：运行测试")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n✅ 配置检查全部通过！")
        print("\n现在可以开始使用了：")
        print("  • /mp preview <文件>  - 本地预览")
        print("  • /mp publish <文件>  - 发布到公众号")
        print("\n💡 提示：运行 /mp help 查看完整使用指南")
    else:
        print("\n\n❌ 步骤 5/5：测试跳过")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n由于连接测试失败，请先解决上述问题后再试。")
        print("\n常见问题：")
        print("  1. API Key 是否正确")
        print("  2. 网络是否能访问对应服务")
        print("  3. 如果使用代理，检查代理设置")


def cmd_help(args):
    """Show help message."""
    print(HELP_MESSAGE)


def check_and_prompt_config():
    """Check config and prompt user if incomplete."""
    is_valid, issues = check_config()

    if not is_valid:
        print("""
⚠️  配置不完整，无法执行命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        print(f"发现 {len(issues)} 个配置问题：\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue['message']}")

        print("""
💡 快速解决：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

方法一（推荐）：让 AI 引导你配置
────────────────────────────────────────────────────────────
直接输入：/mp setup

方法二：手动配置
────────────────────────────────────────────────────────────
1. 编辑配置文件：~/.mp-editor/.env
2. 填入必要的 API 密钥
3. 重新运行命令

详细获取方式：运行 /mp setup 查看
""")
        return False

    return True


def read_content_file(file_path: str) -> str:
    """Read content from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def cmd_polish(args):
    """Polish command: run only the polish node."""
    # Check config first
    if not check_and_prompt_config():
        return

    content = read_content_file(args.file)

    # Import here to ensure env is loaded
    from graphs.nodes.polish_node import polish_node
    from langchain_core.runnables import RunnableConfig

    config = RunnableConfig(metadata={"llm_cfg": args.config or "config/polish_node_cfg.json"})
    result = polish_node(GraphInput(content=content), config)

    output = {
        "title": result.title,
        "abstract": result.abstract,
        "content": result.polished_content
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"Output written to {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_preview(args):
    """Preview command: run polish + cover + md2html, output HTML."""
    # Check config first
    if not check_and_prompt_config():
        return

    content = read_content_file(args.file)

    logger.info("Starting preview pipeline...")

    # Run the full graph except WeChat publishing
    # We can do this by running individual nodes
    from graphs.nodes.polish_node import polish_node
    from graphs.nodes.cover_prompt_node import cover_prompt_node
    from graphs.nodes.image_gen_node import image_gen_node
    from graphs.nodes.md2html_node import md2html_node
    from langchain_core.runnables import RunnableConfig
    from graphs.state import (
        PolishInput, CoverPromptInput, ImageGenInput, Md2HtmlInput
    )

    config = RunnableConfig(metadata={"llm_cfg": "config/polish_node_cfg.json"})

    # Step 1: Polish
    logger.info("Step 1: Polishing article...")
    polish_result = polish_node(PolishInput(content=content), config)
    logger.info(f"  Title: {polish_result.title}")

    # Step 2: Generate cover prompt
    logger.info("Step 2: Generating cover prompt...")
    cover_config = RunnableConfig(metadata={"llm_cfg": "config/cover_prompt_node_cfg.json"})
    cover_prompt_result = cover_prompt_node(
        CoverPromptInput(title=polish_result.title, abstract=polish_result.abstract),
        cover_config
    )
    logger.info(f"  Prompt: {cover_prompt_result.cover_prompt[:100]}...")

    # Step 3: Generate cover image
    logger.info("Step 3: Generating cover image...")
    image_result = image_gen_node(
        ImageGenInput(cover_prompt=cover_prompt_result.cover_prompt),
        RunnableConfig(metadata={})
    )
    logger.info(f"  Image URL: {image_result.cover_image_url[:100]}...")

    # Step 4: Convert to HTML
    logger.info("Step 4: Converting to HTML...")
    html_result = md2html_node(
        Md2HtmlInput(polished_content=polish_result.polished_content),
        RunnableConfig(metadata={})
    )

    # Prepare output
    output_dir = Path(args.output_dir or ".")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save HTML
    html_path = output_dir / "article.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_result.html_content)
    logger.info(f"  HTML saved to {html_path}")

    # Save metadata
    metadata = {
        "title": polish_result.title,
        "abstract": polish_result.abstract,
        "cover_prompt": cover_prompt_result.cover_prompt,
        "cover_image_url": image_result.cover_image_url,
        "html_path": str(html_path)
    }
    meta_path = output_dir / "metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"  Metadata saved to {meta_path}")

    # Save markdown
    md_path = output_dir / "article.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {polish_result.title}\n\n")
        f.write(f"> {polish_result.abstract}\n\n")
        f.write(polish_result.polished_content)
    logger.info(f"  Markdown saved to {md_path}")

    print(f"\nPreview generated in: {output_dir}")
    print(f"  HTML: {html_path}")
    print(f"  Cover Image: {image_result.cover_image_url[:80]}...")


def cmd_publish(args):
    """Publish command: run full pipeline and publish to WeChat."""
    # Check config first
    if not check_and_prompt_config():
        return

    content = read_content_file(args.file)

    logger.info("Starting full publish pipeline...")

    # Run the complete graph
    result = main_graph.invoke({"content": content})

    output = {
        "title": result["title"],
        "abstract": result["abstract"],
        "content": result["content"],
        "cover_image_url": result["cover_image_url"],
        "draft_media_id": result["draft_media_id"]
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"Output written to {args.output}")

    print(f"\nArticle published successfully!")
    print(f"  Title: {result['title']}")
    print(f"  Draft Media ID: {result['draft_media_id']}")
    print(f"  Cover Image: {result['cover_image_url'][:80]}...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MP-Editor: WeChat Official Account article editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  /mp setup                    初始化配置（新手先跑这个）
  /mp help                     查看使用帮助
  /mp polish draft.md          润色文章
  /mp preview draft.md         本地预览
  /mp publish draft.md         发布到公众号

有问题？运行 /mp setup 获取详细帮助。
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="初始化配置向导")
    setup_parser.set_defaults(func=cmd_setup)

    # Help command
    help_parser = subparsers.add_parser("help", help="显示使用帮助")
    help_parser.set_defaults(func=cmd_help)

    # Polish command
    polish_parser = subparsers.add_parser("polish", help="润色文章")
    polish_parser.add_argument("file", help="Markdown 文件路径")
    polish_parser.add_argument("-c", "--config", help="配置文件路径")
    polish_parser.add_argument("-o", "--output", help="输出文件路径")
    polish_parser.set_defaults(func=cmd_polish)

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="本地预览")
    preview_parser.add_argument("file", help="Markdown 文件路径")
    preview_parser.add_argument("-o", "--output-dir", help="输出目录")
    preview_parser.set_defaults(func=cmd_preview)

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="发布到公众号")
    publish_parser.add_argument("file", help="Markdown 文件路径")
    publish_parser.add_argument("-o", "--output", help="输出文件路径")
    publish_parser.set_defaults(func=cmd_publish)

    args = parser.parse_args()

    # Load environment variables
    load_env()

    # If no command, show help
    if not args.command:
        parser.print_help()
        return

    # Run the command
    args.func(args)


if __name__ == "__main__":
    main()
