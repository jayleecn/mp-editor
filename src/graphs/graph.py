"""公众号小编工作流主图编排 - Decoupled from Coze SDK"""
from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.polish_node import polish_node
from graphs.nodes.cover_prompt_node import cover_prompt_node
from graphs.nodes.image_gen_node import image_gen_node
from graphs.nodes.md2html_node import md2html_node
from graphs.nodes.access_token_node import access_token_node
from graphs.nodes.upload_material_node import upload_material_node
from graphs.nodes.upload_article_node import upload_article_node

# 创建状态图，指定入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("polish", polish_node, metadata={"type": "agent", "llm_cfg": "config/polish_node_cfg.json"})
builder.add_node("cover_prompt", cover_prompt_node, metadata={"type": "agent", "llm_cfg": "config/cover_prompt_node_cfg.json"})
builder.add_node("image_gen", image_gen_node)
builder.add_node("md2html", md2html_node)
builder.add_node("access_token", access_token_node)
builder.add_node("upload_material", upload_material_node)
builder.add_node("upload_article", upload_article_node)

# 设置入口点
builder.set_entry_point("polish")

# 添加边
builder.add_edge("polish", "cover_prompt")
builder.add_edge("cover_prompt", "image_gen")
builder.add_edge("image_gen", "md2html")
builder.add_edge("md2html", "access_token")
builder.add_edge("access_token", "upload_material")
builder.add_edge("upload_material", "upload_article")
builder.add_edge("upload_article", END)

# 编译图
main_graph = builder.compile()
