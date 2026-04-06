# MEMORY.md - 财务助手长期记忆

## 核心数据文件

- **持仓数据**：`output/data/positions.json`
  - 格式：JSON，headers + rows
  - 字段：代码、名称、持有金额、持有盈亏、仓位占比、持仓天数、单位成本、最新价等
  - 每次分析持仓相关问题时，必须先读取此文件

## 团队成员

- **金哥**：主要服务对象，前端工程师，稳健型投资者
- **小金**：主持+调度
- **dev/writer/finance/community**：各司其职
