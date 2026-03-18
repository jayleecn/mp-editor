"""上传文章节点"""
import logging
from langchain_core.runnables import RunnableConfig
from graphs.state import UploadArticleInput, UploadArticleOutput
from utils.wechat_client import get_wechat_client

logger = logging.getLogger(__name__)


def upload_article_node(state: UploadArticleInput, config: RunnableConfig) -> UploadArticleOutput:
    """
    title: 上传文章
    desc: 将文章发布到微信公众号草稿箱
    """
    logger.info(f"开始上传文章，标题: {state.title}")

    # 使用微信客户端添加草稿
    client = get_wechat_client()
    draft_media_id = client.add_draft(
        title=state.title,
        content=state.html_content,
        thumb_media_id=state.media_id,
        digest=state.abstract
    )

    logger.info(f"文章上传成功，draft_media_id: {draft_media_id}")

    return UploadArticleOutput(draft_media_id=draft_media_id)
