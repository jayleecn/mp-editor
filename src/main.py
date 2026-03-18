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
from pathlib import Path
from typing import Optional

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


def read_content_file(file_path: str) -> str:
    """Read content from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def cmd_polish(args):
    """Polish command: run only the polish node."""
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
        description="MP-Editor: WeChat Official Account article editor"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Polish command
    polish_parser = subparsers.add_parser("polish", help="Polish an article")
    polish_parser.add_argument("file", help="Path to markdown file")
    polish_parser.add_argument("-c", "--config", help="Path to config file")
    polish_parser.add_argument("-o", "--output", help="Output file path")
    polish_parser.set_defaults(func=cmd_polish)

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Generate local preview")
    preview_parser.add_argument("file", help="Path to markdown file")
    preview_parser.add_argument("-o", "--output-dir", help="Output directory")
    preview_parser.set_defaults(func=cmd_preview)

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish to WeChat")
    publish_parser.add_argument("file", help="Path to markdown file")
    publish_parser.add_argument("-o", "--output", help="Output file path")
    publish_parser.set_defaults(func=cmd_publish)

    args = parser.parse_args()

    # Load environment variables
    load_env()

    # Run the command
    args.func(args)


if __name__ == "__main__":
    main()
