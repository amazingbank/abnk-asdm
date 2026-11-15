---
section: workspace-structure
status: stable
locale: zh-CN
---
# workspace/docs —— 结构树与 locale 叶子层规则

> 结构树（Sprints 各 part / planning 各分区 / sre 各版本目录）**语言无关**；
> locale 标识置于**文档叶子层**（`<目录>/zh-CN/{文档}`）——创作文档按语言分层，证据资产永不分层。

## locale 叶子层分层规则

- 创作文档（sprint 计划 / phase 文档 / planning 设计文档 / ADR / release note）一律入 `<目录>/zh-CN/`
- **永不分层**：`partXX/artifacts/`（证据资产语言无关，en 渲染复用同一物理证据）、`planning/modelB/`（外部资料汇编）、各版本 `artifacts/`（截图等证据）
- 本 README 自身为结构规则文档（结构层，非创作内容），不分层

## en-US 生长规则约定（D4 修订口径）

1. **en 文档存在时路径与 zh-CN 对齐**：路径即 doc id——`partXX/zh-CN/foo.md` 的英文版为 `partXX/en-US/foo.md`，同一文档的两个语言版本靠路径对齐识别，不做注册表
2. **en 是语义重写（D2），不是镜像翻译**：按英语母语者行文组织，允许 en 侧有 zh 没有的文档、也允许 en 侧缺失（缺失即 fallback 到 zh-CN 物理文件）
3. **en 文档「已注册」的标志是 index 层条目**：由 dev portal 数据管线（Part04）的 index 生成器产出，物理文件存在 ≠ 已注册
4. **证据资产语言无关**：物理位置随源文档树（`partXX/artifacts/`），en 文档以相对路径复用同一份证据

## 分层与生长的边界

- **Structural tree is language-neutral; locale lives on the leaf layer.**
- **en-US grows on demand, aligned by path (path IS the doc id), rewritten
  semantically rather than mirrored, with index-level registration done by
  the Part04 data pipeline.**
- 本 Phase（Part03 Phase 5）只落本约定，不翻译任何存量文档；en-US 第一批内容
  由 Part04 Phase 2 触发（dev portal 面向国际社区即「按需」触发事件）
