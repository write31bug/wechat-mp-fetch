# LEARNINGS.md

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted

---

## [LRN-20260403-001] correction

**Logged**: 2026-04-03T09:00:00+08:00
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
小金回答问题时跳步骤、不验证，是LLM"自我纠正盲点"——有能力自纠但不会主动激活

### Details
CMU研究证实（ICLR 2026）：14个主流模型平均64.5%自我错误未被纠正，解决方案是回答前加"Wait"触发词，可减少89.3%盲点。Reddit实测"先问有什么不确定+追问怎么验证"组合错误率降低71%。团队讨论结论：加行为准则4条（耐心/诚实/严谨/自检）到SOUL.md。

### Suggested Action
已在小金/dev/writer/finance/community的SOUL.md加入"行为准则"四条

### Metadata
- Source: user_feedback
- Tags: behavior, response-quality, self-correction
- Pattern-Key: behavior.hasty-response
- Promoted: SOUL.md (行为准则)

---


