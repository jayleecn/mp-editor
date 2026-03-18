"""文章润色节点 - Decoupled from Coze SDK"""
import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from graphs.state import PolishInput, PolishOutput
from llm.service import LLMService, LLMConfig
import logging

logger = logging.getLogger(__name__)

# Default prompts (used when config file not found)
DEFAULT_SYSTEM_PROMPT = """你是微信公众号推文润色专家。请对下面原稿修正错别字，做轻量润色：
- 不新增事实、不删减关键信息
- 不改段落结构
- 语气稳重理性、自然口语化（不营销）

请严格输出一个 JSON（不要 markdown，不要代码块），字段如下：
{
  "title": string,   // <= 20字
  "abstract": string, // <= 50字，第一人称
  "content": string   // 完整公众号文章 markdown（包含标题 H1、分节小标题等）
}"""

DEFAULT_USER_PROMPT = """# 我的推文原文：
{{content}}

请按照上述要求润色，并以JSON格式返回。"""


def _extract_json_from_text(text: str) -> dict:
    """Extract JSON from text, handling various formats."""
    import re

    text = text.strip()
    if not text:
        return {}

    # Try direct JSON parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in code blocks
    code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Try to extract JSON by finding matching braces
    # Use a stack-based approach to find the outermost JSON object
    def find_json_objects(s: str) -> list:
        """Find all potential JSON objects in string."""
        objects = []
        stack = []
        start = -1

        for i, char in enumerate(s):
            if char == '{':
                if not stack:
                    start = i
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start != -1:
                        objects.append(s[start:i+1])
                        start = -1
        return objects

    json_candidates = find_json_objects(text)
    for candidate in json_candidates:
        try:
            parsed = json.loads(candidate)
            # Validate it has the expected fields
            if "title" in parsed or "content" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    # Try the simple first { to last } approach
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            candidate = text[start:end+1]
            parsed = json.loads(candidate)
            if "title" in parsed or "content" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

    # Try regex pattern for JSON with title/abstract/content
    json_pattern = r'\{[\s\S]*?"title"[\s\S]*?"abstract"[\s\S]*?"content"[\s\S]*?\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}


def polish_node(state: PolishInput, config: RunnableConfig) -> PolishOutput:
    """
    title: 文章润色
    desc: 使用大语言模型润色文章，生成标题、摘要和正文
    """
    # Load config file if specified in metadata
    llm_config = {}
    system_prompt = DEFAULT_SYSTEM_PROMPT
    user_prompt_template = DEFAULT_USER_PROMPT

    if config and 'metadata' in config and config['metadata'].get('llm_cfg'):
        cfg_file = config['metadata']['llm_cfg']
        try:
            with open(cfg_file, 'r', encoding='utf-8') as fd:
                _cfg = json.load(fd)
            llm_config = _cfg.get("config", {})
            system_prompt = _cfg.get("sp", DEFAULT_SYSTEM_PROMPT)
            user_prompt_template = _cfg.get("up", DEFAULT_USER_PROMPT)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {cfg_file}, using defaults")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse config file: {e}, using defaults")

    # Render user prompt with Jinja2
    up_tpl = Template(user_prompt_template)
    user_prompt_content = up_tpl.render({"content": state.content})

    # Initialize LLM service (reads LLM_PROVIDER from env)
    service = LLMService()

    # Create messages
    from llm.providers import Message
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_prompt_content)
    ]

    # Call LLM
    logger.info("Calling LLM for article polishing...")
    result_text = service.chat_sync_with_fallback_config(messages, llm_config)
    logger.info(f"LLM response received, length: {len(result_text)}")

    # Parse response
    result_json = _extract_json_from_text(result_text)

    title = result_json.get("title", "")
    abstract = result_json.get("abstract", "")
    polished_content = result_json.get("content", "")

    # Fallback: try to extract from text format if JSON parsing failed
    if not title or not abstract:
        logger.warning(f"JSON parsing failed or incomplete, using fallback extraction")
        logger.debug(f"Raw response (first 500 chars): {result_text[:500]}")

        # Try to find title and abstract from the raw text
        lines = result_text.strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]  # Remove empty lines and strip

        # Look for title in common patterns
        for line in lines:
            # Skip JSON structural characters
            if line in ('{', '}', '[', ']', ','):
                continue
            # Look for title field
            if '"title"' in line or '"title":' in line:
                match = re.search(r'"title"\s*:\s*"([^"]+)"', line)
                if match:
                    title = match.group(1)
                    break
            # If no title field found, use first non-JSON line as title
            elif not title and line and line not in ('{', '}') and not line.startswith('"'):
                title = line.strip('#').strip()

        # Look for abstract in common patterns
        for line in lines:
            if '"abstract"' in line or '"abstract":' in line:
                match = re.search(r'"abstract"\s*:\s*"([^"]+)"', line)
                if match:
                    abstract = match.group(1)
                    break

        if not polished_content:
            # Try to extract content field
            content_match = re.search(r'"content"\s*:\s*"([\s\S]*?)"\s*(?:,|\})', result_text)
            if content_match:
                # Unescape newlines and quotes
                content_text = content_match.group(1)
                content_text = content_text.replace('\\n', '\n').replace('\\"', '"')
                polished_content = content_text
            else:
                polished_content = result_text

    return PolishOutput(
        title=title.strip(),
        abstract=abstract.strip(),
        polished_content=polished_content.strip()
    )
