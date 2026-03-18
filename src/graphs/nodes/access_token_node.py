"""获取AccessToken节点"""
import os
import logging
from langchain_core.runnables import RunnableConfig
from graphs.state import AccessTokenInput, AccessTokenOutput
from utils.wechat_client import get_wechat_client

logger = logging.getLogger(__name__)


def access_token_node(state: AccessTokenInput, config: RunnableConfig) -> AccessTokenOutput:
    """
    title: 获取AccessToken
    desc: 获取微信公众号API的access_token（通过环境变量配置AppID和AppSecret）
    """
    # 检查环境变量
    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")

    if not app_id or not app_secret:
        raise Exception(
            "微信公众号配置缺失！请设置以下环境变量：\n"
            "  - WECHAT_APP_ID: 微信公众号AppID\n"
            "  - WECHAT_APP_SECRET: 微信公众号AppSecret\n"
            "配置方式：\n"
            "  1. 环境变量: export WECHAT_APP_ID=xxx WECHAT_APP_SECRET=xxx\n"
            "  2. .env文件: 在 ~/.mp-editor/.env 中设置"
        )

    logger.info(f"检测到微信配置，AppID: {app_id[:5]}***")

    # 获取access_token
    client = get_wechat_client()
    access_token = client.get_access_token()

    logger.info(f"成功获取access_token: {access_token[:20]}...")

    return AccessTokenOutput(access_token=access_token)
