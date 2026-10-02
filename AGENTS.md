# 仓库导航

公众号编辑 CLI 与 AI skill。普通克隆从仓库根目录用 `.venv/bin/python -m src.main` 执行；`/mp` 是任务写法，参数映射见 [SKILL.md](SKILL.md)。安装和复核步骤见 [README.md](README.md)。

- CLI、配置加载、polish/preview/publish 分派：`src/main.py`。
- 发布图和状态：`src/graphs/graph.py`、`src/graphs/state.py`；preview 在 CLI 中直接调用节点。
- 提示词：`config/polish_node_cfg.json`、`config/cover_prompt_node_cfg.json`。
- 节点：`src/graphs/nodes/`；HTML：`md2html_node.py`。
- 模型：`src/llm/service.py`、`providers.py`、`image_service.py`；微信：`src/utils/wechat_client.py`。
- 模板：`.env.example`；配置：先 `~/.mp-editor/.env`，再当前目录 `.env`，再环境变量。

当前只实现 Aliyun。polish 输出是 JSON，content 字段才是 Markdown。离线入口检查：`--help`、`bash -n scripts/run.sh` 和 `bash -n mp-editor.sh`。实际模型调用与公众号上传需要配置；没有自动化测试套件。
