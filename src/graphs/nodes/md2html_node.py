"""MD转HTML节点 - 微信公众号专用版"""
import os
import re
import logging
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from langchain_core.runnables import RunnableConfig
from graphs.state import Md2HtmlInput, Md2HtmlOutput

logger = logging.getLogger(__name__)

# 主题色
PRIMARY_COLOR = "#0F4C81"
FOREGROUND = "#3f3f3f"
BLOCKQUOTE_BG = "#f7f7f7"
LINK_COLOR = "#576b95"


def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight_code(code: str, lang: str) -> str:
    """代码高亮"""
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
    except:
        lexer = TextLexer()

    formatter = HtmlFormatter(
        style='friendly',
        noclasses=True,
        nowrap=True
    )
    highlighted = highlight(code, lexer, formatter)
    return highlighted


class WeChatMarkdownRenderer:
    """微信公众号专用 Markdown 渲染器"""

    def __init__(self):
        self.footnotes = []
        self.footnote_index = 0
        self.is_first_paragraph = True

    def render(self, text: str) -> str:
        """渲染 Markdown 为微信公众号 HTML"""
        lines = text.split('\n')
        html_parts = []
        i = 0
        in_code_block = False
        code_block = []
        code_lang = ""
        in_blockquote = False
        blockquote_lines = []

        while i < len(lines):
            line = lines[i]

            # 代码块处理
            if line.startswith('```'):
                if in_code_block:
                    code_html = self._render_code_block('\n'.join(code_block), code_lang)
                    html_parts.append(code_html)
                    code_block = []
                    code_lang = ""
                    in_code_block = False
                else:
                    in_code_block = True
                    code_lang = line[3:].strip()
                i += 1
                continue

            if in_code_block:
                code_block.append(line)
                i += 1
                continue

            # 引用块处理
            if line.startswith('>'):
                in_blockquote = True
                blockquote_lines.append(line[1:].strip())
                i += 1
                continue
            elif in_blockquote:
                html_parts.append(self._render_blockquote(blockquote_lines))
                blockquote_lines = []
                in_blockquote = False

            # 空行
            if not line.strip():
                i += 1
                continue

            # 标题
            if line.startswith('#'):
                html_parts.append(self._render_heading(line))
                i += 1
                continue

            # 无序列表
            if line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                    list_items.append(lines[i][2:].strip())
                    i += 1
                html_parts.append(self._render_list(list_items, ordered=False))
                continue

            # 有序列表
            if re.match(r'^\d+\. ', line):
                list_items = []
                while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                    list_items.append(re.sub(r'^\d+\. ', '', lines[i]).strip())
                    i += 1
                html_parts.append(self._render_list(list_items, ordered=True))
                continue

            # 分隔线
            if line.strip() in ['---', '***', '___']:
                html_parts.append(self._render_hr())
                i += 1
                continue

            # 普通段落
            html_parts.append(self._render_paragraph(line))
            i += 1

        # 处理未结束的引用块
        if in_blockquote and blockquote_lines:
            html_parts.append(self._render_blockquote(blockquote_lines))

        return ''.join(html_parts)

    def _render_heading(self, line: str) -> str:
        """渲染标题"""
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not match:
            return self._render_paragraph(line)

        level = len(match.group(1))
        text = self._render_inline(match.group(2))

        if level == 1:
            return ''
        elif level == 2:
            return f'<h2 class="h2" data-heading="true" style="display: table; padding: 0 0.2em; margin: 2.5em auto 1.5em; color: #fff; background: {PRIMARY_COLOR}; font-size: calc(16px * 1.2); font-weight: bold; text-align: center;">{text}</h2>'
        elif level == 3:
            return f'<section style="margin:16px 8px;padding-left:12px;border-left:3px solid {PRIMARY_COLOR};"><span style="font-size:17px;font-weight:bold;color:{FOREGROUND};">{text}</span></section>'
        else:
            return f'<section style="margin:12px 8px;"><span style="font-size:16px;font-weight:bold;color:{PRIMARY_COLOR};">{text}</span></section>'

    def _render_paragraph(self, text: str, first_paragraph: bool = False) -> str:
        """渲染段落"""
        if not text.strip():
            return ''
        content = self._render_inline(text)

        if self.is_first_paragraph:
            self.is_first_paragraph = False
            return f'<p class="p" style="margin: 1.5em 8px; letter-spacing: 0.1em; color: #3f3f3f; margin-top: 0 !important;">{content}</p>'

        return f'<p class="p" style="margin: 1.5em 8px; letter-spacing: 0.1em; color: #3f3f3f;">{content}</p>'

    def _render_blockquote(self, lines: list) -> str:
        """渲染引用块"""
        content = '<br>'.join([self._render_inline(line) for line in lines if line.strip()])
        return f'<blockquote class="blockquote" style="margin-top: 0; margin-right: 0; margin-left: 0; font-style: normal; padding: 1em; border-left: 4px solid {PRIMARY_COLOR}; border-radius: 6px; color: #3f3f3f; background: #f7f7f7; margin-bottom: 1em;"><p class="p" style="display: block; font-size: 1em; letter-spacing: 0.1em; color: #3f3f3f; margin: 0;">{content}</p></blockquote>'

    def _render_list(self, items: list, ordered: bool = False) -> str:
        """渲染列表"""
        items_html = []
        for item in items:
            content = self._render_inline(item)
            prefix = '• ' if not ordered else ''
            items_html.append(f'<li class="listitem" style="display: block; margin: 0.2em 8px; color: #3f3f3f;">{prefix}{content}</li>')

        tag = 'ul' if not ordered else 'ol'
        list_style = 'list-style: circle; padding-left: 1em; margin-left: 0; color: #3f3f3f;' if not ordered else 'padding-left: 1em; margin-left: 0; color: #3f3f3f;'

        return f'<{tag} class="{tag}" style="{list_style}">{"".join(items_html)}</{tag}>'

    def _render_code_block(self, code: str, lang: str) -> str:
        """渲染代码块"""
        try:
            highlighted = highlight_code(code, lang)
        except:
            highlighted = escape_html(code)

        return f'<section style="margin:12px 8px;padding:16px;background:#f6f8fa;border-radius:8px;overflow-x:auto;"><pre style="margin:0;padding:0;white-space:pre-wrap;word-wrap:break-word;"><code style="font-family:Menlo,Monaco,Consolas,monospace;font-size:14px;line-height:1.5;color:#24292e;">{highlighted}</code></pre></section>'

    def _render_hr(self) -> str:
        """渲染分隔线"""
        return f'<section style="margin:16px 0;border-top:1px solid rgba(0,0,0,0.1);"></section>'

    def _render_inline(self, text: str) -> str:
        """渲染行内元素"""
        if not text:
            return ''

        text = text.replace('"', '&quot;')

        # 代码
        text = re.sub(r'`([^`]+)`', r'<code style="font-size:14px;color:#d14;background:rgba(27,31,35,0.05);padding:2px 6px;border-radius:4px;">\g<1></code>', text)

        # 加粗
        text = re.sub(r'\*\*(.+?)\*\*', lambda m: f'<strong style="color: {PRIMARY_COLOR}; font-weight: bold; font-size: inherit;">{m.group(1)}</strong>', text)
        text = re.sub(r'__(.+?)__', lambda m: f'<strong style="color: {PRIMARY_COLOR}; font-weight: bold; font-size: inherit;">{m.group(1)}</strong>', text)

        # 斜体
        text = re.sub(r'\*(.+?)\*', lambda m: f'<em style="font-style: italic;">{m.group(1)}</em>', text)
        text = re.sub(r'_(.+?)_', lambda m: f'<em style="font-style: italic;">{m.group(1)}</em>', text)

        # 链接
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" style="color:{LINK_COLOR};text-decoration:none;">{m.group(1)}</a>', text)

        return text


def md2html_node(state: Md2HtmlInput, config: RunnableConfig) -> Md2HtmlOutput:
    """
    title: MD转HTML
    desc: 将Markdown内容转换为微信公众号友好的HTML格式
    """
    logger.info("开始将 Markdown 转换为微信公众号 HTML")

    renderer = WeChatMarkdownRenderer()
    html_content = renderer.render(state.polished_content)

    final_html = f'''<section style="font-family:-apple-system-font,BlinkMacSystemFont,'Helvetica Neue','PingFang SC','Hiragino Sans GB','Microsoft YaHei UI','Microsoft YaHei',Arial,sans-serif;font-size:16px;line-height:1.75;text-align:left;">
{html_content}
</section>'''

    logger.info(f"Markdown 转 HTML 完成，HTML 长度: {len(final_html)}")

    return Md2HtmlOutput(html_content=final_html)
