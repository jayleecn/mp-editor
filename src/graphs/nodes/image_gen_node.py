"""图像生成节点 - Decoupled from Coze SDK"""
from langchain_core.runnables import RunnableConfig
from graphs.state import ImageGenInput, ImageGenOutput
from llm.image_service import ImageGenService
import logging

logger = logging.getLogger(__name__)


def image_gen_node(state: ImageGenInput, config: RunnableConfig) -> ImageGenOutput:
    """
    title: 图像生成
    desc: 根据提示词生成封面图片
    """
    # Initialize image generation service (reads IMAGE_PROVIDER from env)
    service = ImageGenService()

    # Generate image
    logger.info(f"Generating cover image with prompt: {state.cover_prompt[:100]}...")
    cover_image_url = service.generate_sync(
        prompt=state.cover_prompt,
        size="3024x1296"  # 900:383比例
    )

    logger.info(f"Cover image generated: {cover_image_url[:100]}...")

    return ImageGenOutput(cover_image_url=cover_image_url)
