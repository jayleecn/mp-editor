"""封面提示词生成节点 - Decoupled from Coze SDK"""
import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from graphs.state import CoverPromptInput, CoverPromptOutput
from llm.service import LLMService
import logging

logger = logging.getLogger(__name__)

# Default prompts
DEFAULT_SYSTEM_PROMPT = """你是公众号封面图设计师。基于下面的标题与摘要，生成【一段】完整的 AI 绘画提示词（不要加任何解释、不要 markdown、不要代码块）。要求：
- 适配公众号封面 900:383，主体居中，安全区约60%，方便1:1截取
- 风格简约、专业、有质感
- 禁止任何文字、水印、logo、二维码、UI
- 画面元素 <= 3（主体+最多2个辅助）
- 输出只要提示词正文"""

DEFAULT_USER_PROMPT = """推文标题：{{title}}
推文摘要：{{abstract}}

请根据以上信息生成完整的AI绘画提示词。"""


def cover_prompt_node(state: CoverPromptInput, config: RunnableConfig) -> CoverPromptOutput:
    """
    title: 生成封面提示词
    desc: 根据标题和摘要生成AI绘画提示词
    """
    # Load config file if specified
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
    user_prompt_content = up_tpl.render({
        "title": state.title,
        "abstract": state.abstract
    })

    # Initialize LLM service
    service = LLMService()

    # Create messages
    from llm.providers import Message
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_prompt_content)
    ]

    # Call LLM
    logger.info("Calling LLM for cover prompt generation...")
    result_text = service.chat_sync_with_fallback_config(messages, llm_config)
    logger.info(f"Cover prompt received, length: {len(result_text)}")

    # Clean up the prompt - remove markdown, quotes, etc.
    cover_prompt = result_text.strip()

    # Remove markdown code blocks if present
    import re
    code_block_pattern = r'```[\w]*\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, cover_prompt, re.DOTALL)
    if match:
        cover_prompt = match.group(1).strip()

    # Remove surrounding quotes
    cover_prompt = cover_prompt.strip('"\'"""')

    return CoverPromptOutput(cover_prompt=cover_prompt)
