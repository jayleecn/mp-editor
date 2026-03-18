"""微信公众号API客户端"""
import os
import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class WeChatClient:
    """微信公众号API客户端，支持通过环境变量配置"""

    _instance = None
    _access_token: Optional[str] = None
    _token_expires_at: int = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.app_id = os.getenv("WECHAT_APP_ID", "")
        self.app_secret = os.getenv("WECHAT_APP_SECRET", "")

        if not self.app_id or not self.app_secret:
            logger.warning("微信公众号配置缺失，请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

    def get_access_token(self) -> str:
        """获取微信access_token"""
        if self._access_token and time.time() < self._token_expires_at:
            logger.info("使用缓存的access_token")
            return self._access_token

        if not self.app_id or not self.app_secret:
            raise Exception("微信公众号配置缺失，请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"

        logger.info("正在获取新的access_token...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"获取access_token失败: {data.get('errmsg', data)}")

        self._access_token = data.get("access_token")
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = int(time.time()) + expires_in - 300

        logger.info(f"成功获取access_token，有效期: {expires_in}秒")

        if not self._access_token:
            raise Exception("获取access_token失败: 响应中没有access_token")

        return self._access_token

    def upload_image(self, image_url: str) -> str:
        """上传图片到微信素材库，返回media_id"""
        access_token = self.get_access_token()

        logger.info(f"正在下载图片: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = response.content
        logger.info(f"图片下载成功，大小: {len(image_data)} bytes")

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
        files = {"media": ("cover.jpg", image_data)}

        logger.info("正在上传图片到微信素材库...")
        response = requests.post(url, files=files, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get("errcode", 0) != 0:
            raise Exception(f"上传图片失败: 错误码={data.get('errcode')}, 错误信息={data.get('errmsg')}")

        media_id = data.get("media_id", "")
        logger.info(f"图片上传成功，media_id: {media_id}")

        return media_id

    def add_draft(self, title: str, content: str, thumb_media_id: str, digest: str = "") -> str:
        """添加草稿，返回draft_media_id"""
        import json

        access_token = self.get_access_token()

        logger.info(f"=== 发送给微信的 HTML 内容（前1000字符）===")
        logger.info(content[:1000])
        logger.info("===")

        article = {
            "title": title,
            "author": "",
            "digest": digest,
            "content": content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        json_data = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")

        logger.info(f"正在添加草稿，标题: {title}")
        response = requests.post(url, data=json_data, timeout=15)
        response.raise_for_status()

        data = response.json()

        if data.get("errcode", 0) != 0:
            raise Exception(f"添加草稿失败: 错误码={data.get('errcode')}, 错误信息={data.get('errmsg')}")

        draft_media_id = data.get("media_id", "")
        logger.info(f"草稿添加成功，draft_media_id: {draft_media_id}")

        return draft_media_id


# Global client instance
_wechat_client: Optional[WeChatClient] = None


def get_wechat_client() -> WeChatClient:
    """获取微信公众号客户端实例"""
    global _wechat_client
    if _wechat_client is None:
        _wechat_client = WeChatClient()
    return _wechat_client
