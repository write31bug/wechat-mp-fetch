import sys
sys.path.insert(0, 'E:/openclaw/tasks')
from ask_board import block_task, complete_task

# 3 concrete experiences from dev research
experience = """【经验1】分层记忆架构 — 用分层设计替代单一 context：工作集/短时/长期分层，按需注入上下文，避免 context 溢出。
【经验2】三类记忆分类存储 — 将记忆分为语义/情景/程序三类，语义用向量库检索，情景带时序，程序用知识库管理。
【经验3】会话末摘要写入 — 会话结束时 LLM 提炼关键信息落长期存储，而非全量原始对话存入，减少噪声和 token 浪费。"""

block_task('MEM-R0-DEV', 'dev', '调研完成，等待汇总')
print('block_task done')
complete_task('MEM-R0-DEV', 'dev', experience)
print('complete_task done')
