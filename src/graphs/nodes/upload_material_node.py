"""上传素材节点"""
import logging
from langchain_core.runnables import RunnableConfig
from graphs.state import UploadMaterialInput, UploadMaterialOutput
from utils.wechat_client import get_wechat_client

logger = logging.getLogger(__name__)


def upload_material_node(state: UploadMaterialInput, config: RunnableConfig) -> UploadMaterialOutput:
    """
    title: 上传素材
    desc: 将封面图片上传到微信素材库
    """
    logger.info(f"开始上传素材，图片URL: {state.cover_image_url[:50]}...")

    # 使用微信客户端上传图片
    client = get_wechat_client()
    media_id = client.upload_image(state.cover_image_url)

    logger.info(f"素材上传成功，media_id: {media_id}")

    return UploadMaterialOutput(media_id=media_id)
