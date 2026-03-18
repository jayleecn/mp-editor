"""公众号小编工作流状态定义"""
from typing import Optional
from pydantic import BaseModel, Field


# 全局状态定义
class GlobalState(BaseModel):
    """全局状态定义"""
    # 输入
    content: str = Field(default="", description="用户输入的文章内容")

    # 润色节点输出
    title: str = Field(default="", description="润色后的标题")
    abstract: str = Field(default="", description="润色后的摘要")
    polished_content: str = Field(default="", description="润色后的正文内容")

    # 封面提示词生成节点输出
    cover_prompt: str = Field(default="", description="封面图生成提示词")

    # 图像生成节点输出
    cover_image_url: str = Field(default="", description="生成的封面图URL")

    # MD转HTML节点输出
    html_content: str = Field(default="", description="转换后的HTML内容")

    # 微信API相关
    access_token: str = Field(default="", description="微信API access_token")
    media_id: str = Field(default="", description="上传的图片素材ID")
    draft_media_id: str = Field(default="", description="草稿ID")


# 工作流输入输出定义
class GraphInput(BaseModel):
    """工作流的输入"""
    content: str = Field(..., description="用户输入的文章内容")


class GraphOutput(BaseModel):
    """工作流的输出"""
    title: str = Field(..., description="文章标题")
    abstract: str = Field(..., description="文章摘要")
    content: str = Field(..., description="文章正文")
    cover_image_url: str = Field(..., description="封面图URL")
    draft_media_id: str = Field(..., description="草稿ID，用于标识上传到微信公众号的文章")


# 节点出入参定义

# 润色节点
class PolishInput(BaseModel):
    """文章润色节点的输入"""
    content: str = Field(..., description="用户输入的文章内容")


class PolishOutput(BaseModel):
    """文章润色节点的输出"""
    title: str = Field(..., description="润色后的标题")
    abstract: str = Field(..., description="润色后的摘要")
    polished_content: str = Field(..., description="润色后的正文内容")


# 封面提示词生成节点
class CoverPromptInput(BaseModel):
    """封面提示词生成节点的输入"""
    title: str = Field(..., description="文章标题")
    abstract: str = Field(..., description="文章摘要")


class CoverPromptOutput(BaseModel):
    """封面提示词生成节点的输出"""
    cover_prompt: str = Field(..., description="封面图生成提示词")


# 图像生成节点
class ImageGenInput(BaseModel):
    """图像生成节点的输入"""
    cover_prompt: str = Field(..., description="封面图生成提示词")


class ImageGenOutput(BaseModel):
    """图像生成节点的输出"""
    cover_image_url: str = Field(..., description="生成的封面图URL")


# MD转HTML节点
class Md2HtmlInput(BaseModel):
    """MD转HTML节点的输入"""
    polished_content: str = Field(..., description="润色后的正文内容")


class Md2HtmlOutput(BaseModel):
    """MD转HTML节点的输出"""
    html_content: str = Field(..., description="转换后的HTML内容")


# 获取AccessToken节点
class AccessTokenInput(BaseModel):
    """获取AccessToken节点的输入"""
    pass


class AccessTokenOutput(BaseModel):
    """获取AccessToken节点的输出"""
    access_token: str = Field(..., description="微信API access_token")


# 上传素材节点
class UploadMaterialInput(BaseModel):
    """上传素材节点的输入"""
    access_token: str = Field(..., description="微信API access_token")
    cover_image_url: str = Field(..., description="封面图URL")


class UploadMaterialOutput(BaseModel):
    """上传素材节点的输出"""
    media_id: str = Field(..., description="上传的图片素材ID")


# 上传文章节点
class UploadArticleInput(BaseModel):
    """上传文章节点的输入"""
    access_token: str = Field(..., description="微信API access_token")
    title: str = Field(..., description="文章标题")
    html_content: str = Field(..., description="文章HTML内容")
    media_id: str = Field(..., description="封面图素材ID")
    abstract: str = Field(..., description="文章摘要")


class UploadArticleOutput(BaseModel):
    """上传文章节点的输出"""
    draft_media_id: str = Field(..., description="草稿ID")
