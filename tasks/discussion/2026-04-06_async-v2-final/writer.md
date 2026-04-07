# writer 对「v2 方案修复后」的复审

## 核心结论
**升级**——两个 P1 改进都已到位，v2 相比 v1 有实质提升，值得切换。

## P1 改进验证

- confidence 参考标准：**✅ 已完善**
  三级定义清晰：high = 有数据/第一手经验，medium = 逻辑推导但未实证，low = 跨领域/直觉判断。标准具体可操作，agent 自评时有锚点，不会乱填。main 汇总时对 low 降权也有了依据。

- .md 路径规范：**✅ 已定义**
  `base_path + {agent}.md` 格式明确，`{base_path}/summary.md` 为汇总输出，manifest.json 只做入口不参与状态管理。目录结构干净，不会有歧义。

## 对 writer 的实际价值

1. **confidence 自评让 writer 的声音更可信**：writer 写内容时往往有审美判断但缺数据支撑，medium/low 标注反而显得诚实，main 在汇总时不会被误导。

2. **路径规范让协作更省心**：不需要每次问"我该写哪个路径"，`{base_path}/writer.md` 是唯一答案，降低出错概率。

3. **文件即产出**：.md 直接可读可分享，不需要再转一次格式，这是 writer 最看重的——内容是终点，不是中间物。

## 遗留问题

无实质遗留。以下两点是锦上添花，不影响升级决策：

- manifest.json 仍在 base_path，和 v2"状态全在 DB"的理念有轻微不一致，但作为任务入口文件保留是合理的，无需强制移除
- 若未来 agent 数量增加（如新增 product agent），contributions 表的 agent 字段是否需要扩展为 tags，值得后续注意，但当前不影响

## 最终建议

**立即升级到 v2**。P0（P1 的 WAL + busy_timeout）和两个 P1 改进均已验证通过，writer 支持升级。
