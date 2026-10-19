# 运行环境与同事测试

## 日常使用不需要运行脚本

任何能读取附件或项目文件的 AI 都可以直接使用：

1. 上传或解压整个 Skill 包。
2. 把 `agents/generic-system-prompt.md` 设为项目/助手系统指令；如果平台没有系统指令功能，就在第一条消息中粘贴它。
3. 让 AI 先完整读取 `SKILL.md`，再按任务加载所需参考。
4. 不支持 XLSX/DOCX 时，只用 `product_catalog.jsonl`、`tiktok-operations-extracted.md` 和相关 Markdown。
5. 按 `test-cases.md` 从用例 1 开始测试。

## 可选维护/校验运行时

- Windows 无 Python：在 PowerShell 中运行 `powershell -ExecutionPolicy Bypass -File scripts\validate_bundle.ps1`。
- 有 Python 3.9+：运行 `python scripts/validate_bundle.py` 和 `python scripts/run_fixture_tests.py`。
- 重建产品索引或 DOCX 检索版需要 Python 3.9+，但只使用标准库。
- `quick_validate.py` 属于 Codex Skill Creator，可选；其他平台不需要。

## 平台差异

- 有网页/浏览器工具：允许实时找对标，但必须保存链接和观察时间。
- 无网页工具：要求用户提供链接、视频、转录、截图或平台导出；不得假装已访问。
- 上下文有限：先用精确 SKU 搜索 JSONL，只加载命中行；运营文档用关键词检索导航。
- 不支持 ZIP 内检索：先解压后上传 `SKILL.md`、`agents/generic-system-prompt.md` 和本次需要的参考文件。

## 验收底线

- 精确 SKU，不跨产品混用事实。
- 无实时数据不输出“当前推荐”或正式高分池。
- 仿写先有结构指纹，且通过事实、原创、合规三重质检。
- 不登录、不发布、不上传、不投放、不修改源知识文件，除非用户另外明确授权。
